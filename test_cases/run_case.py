"""
Run a benchmark case and write artifacts under test_cases/<case>/runs/<timestamp>/.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import logging
import re
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from agent.compiler import compile_urdf_report, persist_compile_success_artifacts
from agent.cost import max_cost_usd_from_env, parse_max_cost_usd
from agent.providers.factory import validate_provider_credentials
from agent.providers.openai import DEFAULT_OPENAI_MODEL
from agent.providers.openai_api_surface import (
    classify_provider_failure_kind,
    openai_compaction_mode,
    resolve_openai_api_surface,
    validate_openai_provider_options,
)
from agent.record_persistence import _remove_tree_if_exists
from agent.run_context import (
    _read_logged_cost_totals,
    _relative_to_repo,
)
from agent.single_run import run_from_input_impl
from agent.tools import build_initial_user_content, resolve_image_path
from agent.tui.console_support import ensure_utf8_stdio
from articraft.values import DEFAULT_THINKING_LEVEL, PROVIDER_VALUES, THINKING_LEVEL_VALUES

TEST_CASES_ROOT = Path(__file__).resolve().parent
MANIFEST_SUITE_DIRS = (
    "01_Simple_Functional_10",
    "02_Furniture_10",
)
COMPLEX_CASES_ROOT = TEST_CASES_ROOT / "cases"


@dataclass(frozen=True, slots=True)
class CaseSpec:
    case_id: str
    suite: str | None
    case_dir: Path
    prompt_path: Path
    reference_image: Path | None
    agent_input_file: str | None = None


def _utc_run_token(now: datetime | None = None) -> str:
    instant = now or datetime.now(timezone.utc)
    return instant.strftime("%Y%m%dT%H%M%SZ")


def _read_manifest_rows(manifest_path: Path) -> list[dict[str, str]]:
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _manifest_case_specs(suite_dir: Path) -> list[CaseSpec]:
    manifest_path = suite_dir / "manifest.csv"
    if not manifest_path.is_file():
        return []
    specs: list[CaseSpec] = []
    for row in _read_manifest_rows(manifest_path):
        case_id = (row.get("case_id") or "").strip()
        case_folder = (row.get("case_folder") or "").strip()
        agent_input = (row.get("agent_input_file") or "").strip()
        reference_image = (row.get("reference_image") or "").strip()
        if not case_id or not case_folder or not agent_input:
            continue
        case_dir = (suite_dir / case_folder).resolve()
        prompt_path = (suite_dir / agent_input).resolve()
        ref_path = (suite_dir / reference_image).resolve() if reference_image else None
        specs.append(
            CaseSpec(
                case_id=case_id,
                suite=suite_dir.name,
                case_dir=case_dir,
                prompt_path=prompt_path,
                reference_image=ref_path if ref_path and ref_path.is_file() else None,
                agent_input_file=agent_input,
            )
        )
    return specs


def _read_case_yaml_scalar(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*[\"']?([^\"'\n#]+)", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def _read_case_yaml_prompt_file(case_yaml: Path) -> str | None:
    text = case_yaml.read_text(encoding="utf-8")
    nested = re.search(r"^\s+prompt_file:\s*[\"']?([^\"'\n#]+)", text, flags=re.MULTILINE)
    if nested:
        return nested.group(1).strip()
    return _read_case_yaml_scalar(text, "prompt_file")


def _complex_case_specs() -> list[CaseSpec]:
    specs: list[CaseSpec] = []
    if not COMPLEX_CASES_ROOT.is_dir():
        return specs
    for case_dir in sorted(path for path in COMPLEX_CASES_ROOT.iterdir() if path.is_dir()):
        case_yaml = case_dir / "case.yaml"
        if not case_yaml.is_file():
            continue
        text = case_yaml.read_text(encoding="utf-8")
        case_id = _read_case_yaml_scalar(text, "case_id") or case_dir.name
        prompt_name = _read_case_yaml_prompt_file(case_yaml)
        if not prompt_name:
            for candidate in ("prompt_en.md", "prompt_en.txt", "prompt_zh.md"):
                if (case_dir / candidate).is_file():
                    prompt_name = candidate
                    break
        if not prompt_name:
            continue
        prompt_path = (case_dir / prompt_name).resolve()
        reference_image = _discover_reference_image(case_dir, case_id)
        specs.append(
            CaseSpec(
                case_id=case_id,
                suite="cases",
                case_dir=case_dir.resolve(),
                prompt_path=prompt_path,
                reference_image=reference_image,
                agent_input_file=prompt_name,
            )
        )
    return specs


def _discover_reference_image(case_dir: Path, case_id: str) -> Path | None:
    prefix = case_id.split("_", 1)[0]
    numbered = case_dir / f"{prefix}.png"
    if numbered.is_file():
        return numbered.resolve()
    matches = sorted(case_dir.glob("*.png"))
    return matches[0].resolve() if matches else None


def _all_case_specs() -> list[CaseSpec]:
    specs: list[CaseSpec] = []
    for suite_name in MANIFEST_SUITE_DIRS:
        specs.extend(_manifest_case_specs(TEST_CASES_ROOT / suite_name))
    specs.extend(_complex_case_specs())
    return specs


def list_case_specs() -> list[CaseSpec]:
    return _all_case_specs()


def case_run_ref(spec: CaseSpec) -> str:
    return spec.case_dir.relative_to(TEST_CASES_ROOT).as_posix()


def _resolve_case_ref(case_ref: str, *, suite_hint: str | None) -> CaseSpec:
    normalized = case_ref.strip().replace("\\", "/")
    if not normalized:
        raise ValueError("Case reference is required.")

    candidate_paths: list[Path] = []
    direct = Path(normalized)
    if direct.is_absolute():
        candidate_paths.append(direct)
    else:
        candidate_paths.extend(
            [
                (Path.cwd() / normalized).resolve(),
                (TEST_CASES_ROOT / normalized).resolve(),
            ]
        )

    for candidate in candidate_paths:
        if candidate.is_dir():
            return _case_spec_from_directory(candidate)

    specs = _all_case_specs()
    if suite_hint:
        specs = [
            spec for spec in specs if spec.suite == suite_hint or spec.suite == suite_hint.strip()
        ]

    exact = [spec for spec in specs if spec.case_id == normalized]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        suites = ", ".join(sorted({spec.suite or "" for spec in exact}))
        raise ValueError(f"Case id {normalized!r} is ambiguous across suites: {suites}")

    folder_matches = [
        spec
        for spec in specs
        if spec.case_dir.name == Path(normalized).name
        or spec.case_dir.as_posix().endswith(normalized)
    ]
    if len(folder_matches) == 1:
        return folder_matches[0]

    raise ValueError(f"Unknown test case: {case_ref}")


def _case_spec_from_directory(case_dir: Path) -> CaseSpec:
    resolved = case_dir.resolve()
    for spec in _all_case_specs():
        if spec.case_dir == resolved:
            return spec

    prompt_candidates = [
        resolved / name
        for name in ("prompt_en.txt", "prompt_en.md", "prompt_zh.md", "prompt_zh.txt")
        if (resolved / name).is_file()
    ]
    if not prompt_candidates:
        raise ValueError(f"No prompt file found under {resolved}")

    case_yaml = resolved / "case.yaml"
    case_id = resolved.name
    if case_yaml.is_file():
        text = case_yaml.read_text(encoding="utf-8")
        case_id = _read_case_yaml_scalar(text, "case_id") or case_id
        prompt_name = _read_case_yaml_prompt_file(case_yaml)
        if prompt_name and (resolved / prompt_name).is_file():
            prompt_path = (resolved / prompt_name).resolve()
        else:
            prompt_path = prompt_candidates[0].resolve()
    else:
        prompt_path = prompt_candidates[0].resolve()

    suite = None
    for parent in resolved.parents:
        if parent.parent == TEST_CASES_ROOT and parent.name in MANIFEST_SUITE_DIRS:
            suite = parent.name
            break
        if parent == COMPLEX_CASES_ROOT:
            suite = "cases"
            break

    return CaseSpec(
        case_id=case_id,
        suite=suite,
        case_dir=resolved,
        prompt_path=prompt_path,
        reference_image=_discover_reference_image(resolved, case_id),
        agent_input_file=prompt_path.name,
    )


def _copytree(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _run_observability_fields(
    *,
    args: argparse.Namespace,
    status: str,
    message: str | None,
    cost_path: Path | None,
    duration_seconds: float | None,
) -> dict[str, Any]:
    tokens: dict[str, int] | None = None
    total_cost: float | None = None
    if cost_path is not None and cost_path.is_file():
        tokens, total_cost = _read_logged_cost_totals(cost_path)

    fields: dict[str, Any] = {
        "thinking_level": args.thinking,
    }
    if args.provider == "openai":
        fields["openai_api"] = args.openai_api
        fields["openai_transport"] = args.openai_transport
        fields["compaction_mode"] = openai_compaction_mode(args.openai_api)
    if duration_seconds is not None:
        fields["duration_seconds"] = round(duration_seconds, 3)
    if total_cost is not None:
        fields["total_cost_usd"] = total_cost
    if tokens:
        for key in ("total_tokens", "cached_tokens", "prompt_tokens"):
            value = tokens.get(key)
            if isinstance(value, int):
                fields[key] = value
    failure_kind = classify_provider_failure_kind(status=status, message=message)
    if failure_kind:
        fields["failure_kind"] = failure_kind
    return fields


def _materialize_case_compile(
    *,
    model_path: Path,
    artifact_dir: Path,
    target: str,
) -> dict[str, Any]:
    report = compile_urdf_report(model_path, target=target, ignore_geom_qc=target == "visual")
    urdf_path = artifact_dir / "model.urdf"
    persist_compile_success_artifacts(
        urdf_xml=report.urdf_xml,
        urdf_out=urdf_path,
        outputs_root=artifact_dir,
        previous_sig=None,
    )
    compile_report = {
        "target": target,
        "warnings": list(report.warnings),
        "signal_bundle": report.signal_bundle.to_dict(),
        "model_urdf": urdf_path.name,
    }
    _write_json(artifact_dir / "compile_report.json", compile_report)
    return compile_report


async def _run_case(args: argparse.Namespace) -> int:
    try:
        case = _resolve_case_ref(args.case_ref, suite_hint=args.suite)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not case.prompt_path.is_file():
        print(f"Prompt file not found: {case.prompt_path}", file=sys.stderr)
        return 1

    prompt_text = case.prompt_path.read_text(encoding="utf-8").strip()
    if not prompt_text:
        print(f"Prompt file is empty: {case.prompt_path}", file=sys.stderr)
        return 1

    image_override = args.image
    reference_image = case.reference_image
    try:
        image_path = resolve_image_path(
            image_override or (str(reference_image) if reference_image else None),
            provider=args.provider,
        )
    except Exception as exc:
        print(f"Failed to load reference image: {exc}", file=sys.stderr)
        return 1

    try:
        validate_provider_credentials(args.provider)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    repo_root = args.repo_root.resolve()
    run_token = _utc_run_token()
    artifact_dir = (case.case_dir / "runs" / run_token).resolve()
    user_content = build_initial_user_content(prompt_text, image_path=image_path)
    run_started = time.monotonic()

    outcome = await run_from_input_impl(
        user_content,
        prompt_text=prompt_text,
        display_prompt=prompt_text,
        repo_root=repo_root,
        image_path=image_path,
        provider=args.provider,
        model_id=args.model,
        openai_transport=args.openai_transport,
        openai_api=args.openai_api,
        thinking_level=args.thinking,
        max_turns=args.max_turns,
        system_prompt_path=args.system_prompt,
        sdk_package="sdk",
        openai_reasoning_summary="auto",
        max_cost_usd=args.max_cost_usd,
        collection="workbench",
        record_id=f"bench_{case.case_id}_{run_token}".lower(),
        run_id=f"case_{case.case_id}_{run_token}".lower(),
        persist_run_metadata=False,
        persist_run_result=False,
        persist_record=False,
        cleanup_staging_dir=False,
    )

    duration_seconds = time.monotonic() - run_started

    staging_dir = outcome.staging_dir
    if staging_dir is None or not staging_dir.exists():
        summary = {
            "case_id": case.case_id,
            "suite": case.suite,
            "case_dir": _relative_to_repo(case.case_dir, repo_root),
            "prompt_file": case.agent_input_file or case.prompt_path.name,
            "reference_image": (
                _relative_to_repo(reference_image, repo_root) if reference_image else None
            ),
            "run_id": outcome.run_id,
            "record_id": outcome.record_id,
            "status": outcome.status,
            "message": outcome.message,
            "artifact_dir": _relative_to_repo(artifact_dir, repo_root),
            "provider": outcome.provider,
            "model_id": outcome.model_id,
            **_run_observability_fields(
                args=args,
                status=outcome.status,
                message=outcome.message,
                cost_path=None,
                duration_seconds=duration_seconds,
            ),
        }
        _write_json(artifact_dir / "run_summary.json", summary)
        print(json.dumps(summary, indent=2))
        return outcome.exit_code or 1

    try:
        _copytree(staging_dir, artifact_dir)
    finally:
        await asyncio.to_thread(_remove_tree_if_exists, staging_dir)

    model_path = artifact_dir / "model.py"
    compile_payload: dict[str, Any] | None = None
    compile_error: str | None = None
    if outcome.status == "success" and model_path.is_file():
        try:
            compile_payload = _materialize_case_compile(
                model_path=model_path,
                artifact_dir=artifact_dir,
                target=args.compile_target,
            )
        except Exception as exc:
            compile_error = str(exc)

    cost_path = artifact_dir / "cost.json"

    summary: dict[str, Any] = {
        "case_id": case.case_id,
        "suite": case.suite,
        "case_dir": _relative_to_repo(case.case_dir, repo_root),
        "prompt_file": case.agent_input_file or case.prompt_path.name,
        "reference_image": (
            _relative_to_repo(reference_image, repo_root) if reference_image else None
        ),
        "image_used": _relative_to_repo(image_path, repo_root) if image_path else None,
        "run_id": outcome.run_id,
        "record_id": outcome.record_id,
        "status": outcome.status,
        "message": outcome.message,
        "artifact_dir": _relative_to_repo(artifact_dir, repo_root),
        "provider": outcome.provider,
        "model_id": outcome.model_id,
        "turn_count": outcome.turn_count,
        "tool_call_count": outcome.tool_call_count,
        "compile_attempt_count": outcome.compile_attempt_count,
        "compile_target": args.compile_target,
        "compile_error": compile_error,
        **_run_observability_fields(
            args=args,
            status=outcome.status,
            message=outcome.message,
            cost_path=cost_path,
            duration_seconds=duration_seconds,
        ),
    }
    if compile_payload is not None:
        summary["compile_warnings"] = compile_payload.get("warnings", [])

    _write_json(artifact_dir / "run_summary.json", summary)
    print(json.dumps(summary, indent=2))
    if compile_error:
        print(f"Compile failed after export: {compile_error}", file=sys.stderr)
        return 3 if outcome.exit_code == 0 else outcome.exit_code
    return outcome.exit_code


def _list_cases() -> int:
    for spec in _all_case_specs():
        suite = spec.suite or "?"
        print(f"{spec.case_id}\t{suite}\t{spec.case_dir.relative_to(TEST_CASES_ROOT)}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an Articraft benchmark case into test_cases/<case>/runs/<timestamp>/."
    )
    parser.add_argument(
        "case_ref",
        nargs="?",
        help="Case id (S01, F03, 01_articulated_desk_lamp), folder path, or manifest case_folder.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List known benchmark cases and exit.",
    )
    parser.add_argument(
        "--suite",
        default=None,
        help="Disambiguate a case id when it appears in multiple suites.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=TEST_CASES_ROOT.parent,
        help="Articraft repository root.",
    )
    parser.add_argument("--image", default=None, help="Override the case reference image.")
    parser.add_argument(
        "--provider",
        default="openai",
        choices=PROVIDER_VALUES,
        help="LLM provider.",
    )
    parser.add_argument("--model", default=DEFAULT_OPENAI_MODEL, help="Model id.")
    parser.add_argument(
        "--openai-transport",
        default="http",
        choices=["http", "websocket"],
        help="OpenAI transport mode.",
    )
    parser.add_argument(
        "--openai-api",
        default=None,
        choices=["responses", "chat_completions"],
        help="OpenAI API surface for --provider openai. Defaults to responses.",
    )
    parser.add_argument(
        "--thinking",
        default=DEFAULT_THINKING_LEVEL,
        choices=THINKING_LEVEL_VALUES,
        help="Thinking budget level.",
    )
    parser.add_argument("--max-turns", type=int, default=None)
    parser.add_argument("--max-cost-usd", type=float, default=None)
    parser.add_argument(
        "--system-prompt",
        default="designer_system_prompt.txt",
        help="System prompt path or generated prompt name.",
    )
    parser.add_argument(
        "--compile-target",
        default="visual",
        choices=("visual", "full"),
        help="Compile target for exported artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_stdio()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    load_dotenv()

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list:
        return _list_cases()
    if not args.case_ref:
        parser.error("case_ref is required unless --list is used.")

    try:
        args.max_cost_usd = (
            parse_max_cost_usd(args.max_cost_usd, label="--max-cost-usd")
            if args.max_cost_usd is not None
            else max_cost_usd_from_env()
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.provider != "openai" and args.openai_transport != "http":
        print("--openai-transport is only supported for --provider openai.", file=sys.stderr)
        return 1

    try:
        args.openai_api = validate_openai_provider_options(
            provider=args.provider,
            openai_api=resolve_openai_api_surface(cli_value=args.openai_api),
            openai_transport=args.openai_transport,
            cli_openai_api=args.openai_api,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return asyncio.run(_run_case(args))


if __name__ == "__main__":
    raise SystemExit(main())
