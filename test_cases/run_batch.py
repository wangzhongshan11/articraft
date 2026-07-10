"""
Run numbered benchmark cases sequentially via test_cases/run_case.py.
"""

from __future__ import annotations

import argparse
import json
import logging
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO

from dotenv import load_dotenv

from agent.cost import max_cost_usd_from_env, parse_max_cost_usd
from agent.providers.factory import validate_provider_credentials
from agent.providers.openai import DEFAULT_OPENAI_MODEL
from agent.providers.openai_api_surface import (
    resolve_openai_api_surface,
    validate_openai_provider_options,
)
from agent.tui.console_support import ensure_utf8_stdio, utf8_subprocess_env
from articraft.values import DEFAULT_THINKING_LEVEL, PROVIDER_VALUES, THINKING_LEVEL_VALUES

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from run_case import (  # noqa: E402
    TEST_CASES_ROOT,
    CaseSpec,
    _utc_run_token,
    case_run_ref,
    list_case_specs,
)

RUN_CASE_SCRIPT = _SCRIPT_DIR / "run_case.py"
BATCH_RUNS_ROOT = TEST_CASES_ROOT / "batch_runs"
TERMINAL_BATCH_STATUSES = frozenset({"success", "failed", "agent_ok_compile_fail"})

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class BatchCasePlan:
    index: int
    spec: CaseSpec
    case_ref: str


@dataclass
class CaseRunOutcome:
    batch_status: str
    exit_code: int | None
    run_summary_path: str | None
    artifact_dir: str | None
    run_status: str | None
    message: str | None
    compile_error: str | None
    duration_seconds: float | None
    started_at: str
    finished_at: str | None
    stdout_path: str | None
    stderr_path: str | None


class _BatchRunner:
    def __init__(self) -> None:
        self._child: subprocess.Popen[str] | None = None
        self._interrupted = False

    def install_signal_handlers(self) -> None:
        def _handle(signum: int, _frame: object) -> None:
            self._interrupted = True
            logger.warning("Received signal %s; stopping current case.", signum)
            if self._child is not None and self._child.poll() is None:
                self._child.terminate()

        signal.signal(signal.SIGINT, _handle)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, _handle)

    def run_case_subprocess(self, argv: list[str]) -> subprocess.CompletedProcess[str]:
        self._child = subprocess.Popen(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=utf8_subprocess_env(),
        )
        stdout, stderr = self._child.communicate()
        returncode = self._child.returncode
        self._child = None
        return subprocess.CompletedProcess(argv, returncode, stdout, stderr)

    @property
    def interrupted(self) -> bool:
        return self._interrupted


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object JSON in {path}")
    return payload


def _parse_case_indices(expression: str, *, max_index: int) -> list[int]:
    expr = expression.strip()
    if not expr:
        raise ValueError("--cases expression is empty.")
    selected: set[int] = set()
    for raw_part in expr.split(","):
        part = raw_part.strip()
        if not part:
            continue
        if "-" in part:
            left_text, right_text = part.split("-", 1)
            start = int(left_text.strip())
            end = int(right_text.strip())
            if start > end:
                raise ValueError(f"Invalid case range: {part!r}")
            selected.update(range(start, end + 1))
            continue
        selected.add(int(part))

    if not selected:
        raise ValueError("--cases did not select any indices.")

    invalid = sorted(index for index in selected if index < 1 or index > max_index)
    if invalid:
        raise ValueError(
            f"Case indices out of range 1-{max_index}: {', '.join(str(i) for i in invalid)}"
        )
    return sorted(selected)


def _numbered_plans(indices: list[int]) -> list[BatchCasePlan]:
    specs = list_case_specs()
    if not specs:
        raise ValueError("No benchmark cases found.")
    plans: list[BatchCasePlan] = []
    for index in indices:
        plans.append(
            BatchCasePlan(
                index=index,
                spec=specs[index - 1],
                case_ref=case_run_ref(specs[index - 1]),
            )
        )
    return plans


def _batch_status_for_exit(exit_code: int | None, *, interrupted: bool) -> str:
    if interrupted:
        return "interrupted"
    if exit_code == 0:
        return "success"
    if exit_code == 3:
        return "agent_ok_compile_fail"
    return "failed"


def _snapshot_run_dirs(case_dir: Path) -> set[str]:
    runs_root = case_dir / "runs"
    if not runs_root.is_dir():
        return set()
    return {path.name for path in runs_root.iterdir() if path.is_dir()}


def _resolve_run_summary(
    case_dir: Path,
    before_dirs: set[str],
) -> tuple[Path | None, dict[str, Any] | None]:
    runs_root = case_dir / "runs"
    if not runs_root.is_dir():
        return None, None

    candidates = [
        path for path in runs_root.iterdir() if path.is_dir() and path.name not in before_dirs
    ]
    if not candidates:
        candidates = [path for path in runs_root.iterdir() if path.is_dir()]
    if not candidates:
        return None, None

    run_dir = max(candidates, key=lambda path: path.stat().st_mtime)
    summary_path = run_dir / "run_summary.json"
    if not summary_path.is_file():
        return None, None
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return summary_path, None
    if not isinstance(payload, dict):
        return summary_path, None
    return summary_path, payload


def _relative_repo(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _run_options_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "provider": args.provider,
        "model": args.model,
        "thinking": args.thinking,
        "openai_transport": args.openai_transport,
        "system_prompt": args.system_prompt,
        "compile_target": args.compile_target,
        "repo_root": str(args.repo_root.resolve()),
    }
    if args.image is not None:
        payload["image"] = args.image
    if args.openai_api is not None:
        payload["openai_api"] = args.openai_api
    if args.max_turns is not None:
        payload["max_turns"] = args.max_turns
    if args.max_cost_usd is not None:
        payload["max_cost_usd"] = args.max_cost_usd
    payload["delay_seconds"] = args.delay_seconds
    payload["delay_on_failure"] = args.delay_on_failure
    payload["stop_on_error"] = args.stop_on_error
    return payload


def _build_run_case_argv(args: argparse.Namespace, case_ref: str) -> list[str]:
    argv = [
        sys.executable,
        str(RUN_CASE_SCRIPT),
        case_ref,
        "--repo-root",
        str(args.repo_root.resolve()),
        "--provider",
        args.provider,
        "--model",
        args.model,
        "--openai-transport",
        args.openai_transport,
        "--thinking",
        args.thinking,
        "--system-prompt",
        args.system_prompt,
        "--compile-target",
        args.compile_target,
    ]
    if args.image is not None:
        argv.extend(["--image", args.image])
    if args.openai_api is not None:
        argv.extend(["--openai-api", args.openai_api])
    if args.max_turns is not None:
        argv.extend(["--max-turns", str(args.max_turns)])
    if args.max_cost_usd is not None:
        argv.extend(["--max-cost-usd", str(args.max_cost_usd)])
    return argv


def _append_log(handle: TextIO, header: str, body: str) -> None:
    handle.write(f"\n{'=' * 72}\n{header}\n{'=' * 72}\n")
    if body:
        handle.write(body)
        if not body.endswith("\n"):
            handle.write("\n")
    handle.flush()


def _case_entry_from_outcome(
    plan: BatchCasePlan,
    outcome: CaseRunOutcome,
) -> dict[str, Any]:
    return {
        "index": plan.index,
        "case_id": plan.spec.case_id,
        "suite": plan.spec.suite,
        "case_ref": plan.case_ref,
        "batch_status": outcome.batch_status,
        "exit_code": outcome.exit_code,
        "run_summary_path": outcome.run_summary_path,
        "artifact_dir": outcome.artifact_dir,
        "run_status": outcome.run_status,
        "message": outcome.message,
        "compile_error": outcome.compile_error,
        "duration_seconds": outcome.duration_seconds,
        "started_at": outcome.started_at,
        "finished_at": outcome.finished_at,
        "stdout_path": outcome.stdout_path,
        "stderr_path": outcome.stderr_path,
    }


def _summarize_cases(case_entries: list[dict[str, Any]]) -> dict[str, int]:
    totals = {
        "planned": len(case_entries),
        "success": 0,
        "failed": 0,
        "agent_ok_compile_fail": 0,
        "interrupted": 0,
        "pending": 0,
        "skipped": 0,
    }
    for entry in case_entries:
        status = str(entry.get("batch_status") or "pending")
        if status in totals:
            totals[status] += 1
        else:
            totals["pending"] += 1
    return totals


def _batch_overall_status(case_entries: list[dict[str, Any]], *, interrupted: bool) -> str:
    if interrupted:
        return "interrupted"
    if any(entry.get("batch_status") == "pending" for entry in case_entries):
        return "running"
    return "completed"


def _resolve_batch_dir(args: argparse.Namespace) -> Path:
    batch_id = args.batch_id or _utc_run_token()
    args.batch_id = batch_id
    return BATCH_RUNS_ROOT / batch_id


def _find_resumable_batch_dir() -> Path | None:
    if not BATCH_RUNS_ROOT.is_dir():
        return None
    candidates: list[Path] = []
    for child in BATCH_RUNS_ROOT.iterdir():
        if not child.is_dir():
            continue
        summary_path = child / "batch_summary.json"
        if not summary_path.is_file():
            continue
        try:
            summary = _load_json(summary_path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        entries = summary.get("cases")
        if not isinstance(entries, list):
            continue
        has_pending = any(
            isinstance(entry, dict)
            and entry.get("batch_status") not in TERMINAL_BATCH_STATUSES | {"skipped"}
            for entry in entries
        )
        if has_pending or summary.get("status") == "running":
            candidates.append(summary_path)
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime).parent


def _apply_run_options(args: argparse.Namespace, run_options: dict[str, Any]) -> None:
    for key, value in run_options.items():
        if key in {"delay_seconds", "delay_on_failure", "stop_on_error"}:
            setattr(args, key, value)
            continue
        if not hasattr(args, key):
            continue
        if key == "repo_root":
            setattr(args, key, Path(str(value)).resolve())
            continue
        setattr(args, key, value)


def _load_resume_state(
    batch_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    manifest_path = batch_dir / "batch_manifest.json"
    summary_path = batch_dir / "batch_summary.json"
    if not manifest_path.is_file():
        raise ValueError(f"Missing batch manifest: {manifest_path}")
    manifest = _load_json(manifest_path)
    if summary_path.is_file():
        summary = _load_json(summary_path)
        cases = summary.get("cases")
        if isinstance(cases, list):
            return manifest, summary, [entry for entry in cases if isinstance(entry, dict)]
    planned_cases = manifest.get("cases")
    if not isinstance(planned_cases, list):
        raise ValueError(f"Invalid cases list in {manifest_path}")
    entries = [
        {
            "index": entry.get("index"),
            "case_id": entry.get("case_id"),
            "suite": entry.get("suite"),
            "case_ref": entry.get("case_ref"),
            "batch_status": "pending",
            "exit_code": None,
            "run_summary_path": None,
            "artifact_dir": None,
            "run_status": None,
            "message": None,
            "compile_error": None,
            "duration_seconds": None,
            "started_at": None,
            "finished_at": None,
            "stdout_path": None,
            "stderr_path": None,
        }
        for entry in planned_cases
        if isinstance(entry, dict)
    ]
    summary = {
        "batch_id": manifest.get("batch_id"),
        "status": "running",
        "created_at": manifest.get("created_at"),
        "updated_at": _utc_now_iso(),
        "run_options": manifest.get("run_options"),
        "cases": entries,
        "totals": _summarize_cases(entries),
    }
    return manifest, summary, entries


def _plans_from_summary_entries(entries: list[dict[str, Any]]) -> list[BatchCasePlan]:
    specs = list_case_specs()
    plans: list[BatchCasePlan] = []
    for entry in entries:
        index = entry.get("index")
        if not isinstance(index, int):
            continue
        if index < 1 or index > len(specs):
            continue
        spec = specs[index - 1]
        case_ref = str(entry.get("case_ref") or case_run_ref(spec))
        plans.append(BatchCasePlan(index=index, spec=spec, case_ref=case_ref))
    return plans


def _list_cases_numbered() -> int:
    for index, spec in enumerate(list_case_specs(), start=1):
        print(f"{index:02d}\t{spec.case_id}\t{case_run_ref(spec)}")
    return 0


def _validate_run_args(args: argparse.Namespace) -> int | None:
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

    try:
        validate_provider_credentials(args.provider)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run numbered benchmark cases sequentially via test_cases/run_case.py."
    )
    parser.add_argument(
        "--cases",
        default=None,
        help="Case indices to run (default: all). Example: 1-30,3,5-10.",
    )
    parser.add_argument("--list", action="store_true", help="List numbered benchmark cases.")
    parser.add_argument(
        "--batch-id",
        default=None,
        help="Batch output directory name under test_cases/batch_runs/.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned cases and exit.")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume an existing batch directory (requires --batch-id or latest incomplete batch).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=TEST_CASES_ROOT.parent,
        help="Articraft repository root.",
    )
    parser.add_argument("--image", default=None, help="Override each case reference image.")
    parser.add_argument("--provider", default="openai", choices=PROVIDER_VALUES)
    parser.add_argument("--model", default=DEFAULT_OPENAI_MODEL)
    parser.add_argument(
        "--openai-transport",
        default="http",
        choices=["http", "websocket"],
    )
    parser.add_argument(
        "--openai-api",
        default=None,
        choices=["responses", "chat_completions"],
    )
    parser.add_argument(
        "--thinking",
        default=DEFAULT_THINKING_LEVEL,
        choices=THINKING_LEVEL_VALUES,
    )
    parser.add_argument("--max-turns", type=int, default=None)
    parser.add_argument("--max-cost-usd", type=float, default=None)
    parser.add_argument("--system-prompt", default="designer_system_prompt.txt")
    parser.add_argument("--compile-target", default="visual", choices=("visual", "full"))
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=0.0,
        help="Seconds to wait after each case before starting the next.",
    )
    parser.add_argument(
        "--delay-on-failure",
        type=float,
        default=120.0,
        help="Extra seconds to wait after a failed case.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop the batch after the first non-zero case exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_stdio()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    load_dotenv()

    parser = _build_parser()
    args = parser.parse_args(argv)
    args.repo_root = args.repo_root.resolve()

    if args.list:
        return _list_cases_numbered()

    specs = list_case_specs()
    if not specs:
        print("No benchmark cases found.", file=sys.stderr)
        return 1

    if args.resume:
        batch_dir = _resolve_batch_dir(args) if args.batch_id else _find_resumable_batch_dir()
        if batch_dir is None:
            print("No resumable batch directory found.", file=sys.stderr)
            return 1
        args.batch_id = batch_dir.name
    else:
        batch_dir = _resolve_batch_dir(args)

    manifest_path = batch_dir / "batch_manifest.json"
    summary_path = batch_dir / "batch_summary.json"
    log_path = batch_dir / "batch.log"
    case_logs_dir = batch_dir / "case_logs"

    if args.resume:
        try:
            manifest, summary, case_entries = _load_resume_state(batch_dir)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        run_options = manifest.get("run_options")
        if isinstance(run_options, dict):
            _apply_run_options(args, run_options)
        plans = _plans_from_summary_entries(case_entries)
        if not plans:
            print("Resume batch has no planned cases.", file=sys.stderr)
            return 1
    else:
        try:
            indices = (
                _parse_case_indices(args.cases, max_index=len(specs))
                if args.cases is not None
                else list(range(1, len(specs) + 1))
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        plans = _numbered_plans(indices)
        case_entries = [
            {
                "index": plan.index,
                "case_id": plan.spec.case_id,
                "suite": plan.spec.suite,
                "case_ref": plan.case_ref,
                "batch_status": "pending",
                "exit_code": None,
                "run_summary_path": None,
                "artifact_dir": None,
                "run_status": None,
                "message": None,
                "compile_error": None,
                "duration_seconds": None,
                "started_at": None,
                "finished_at": None,
                "stdout_path": None,
                "stderr_path": None,
            }
            for plan in plans
        ]
        manifest = {
            "batch_id": args.batch_id,
            "created_at": _utc_now_iso(),
            "repo_root": str(args.repo_root),
            "cases": [
                {
                    "index": plan.index,
                    "case_id": plan.spec.case_id,
                    "suite": plan.spec.suite,
                    "case_ref": plan.case_ref,
                }
                for plan in plans
            ],
            "run_options": _run_options_payload(args),
        }
        summary = {
            "batch_id": args.batch_id,
            "status": "running",
            "created_at": manifest["created_at"],
            "updated_at": _utc_now_iso(),
            "run_options": manifest["run_options"],
            "cases": case_entries,
            "totals": _summarize_cases(case_entries),
        }

    if args.dry_run:
        for plan in plans:
            entry = next(item for item in case_entries if item.get("index") == plan.index)
            status = entry.get("batch_status", "pending")
            print(f"{plan.index:02d}\t{plan.spec.case_id}\t{plan.case_ref}\t{status}")
        return 0

    validation_error = _validate_run_args(args)
    if validation_error is not None:
        return validation_error

    if not args.resume:
        batch_dir.mkdir(parents=True, exist_ok=True)
        _write_json(manifest_path, manifest)

    runner = _BatchRunner()
    runner.install_signal_handlers()

    entries_by_index = {int(entry["index"]): entry for entry in case_entries if "index" in entry}

    with log_path.open("a", encoding="utf-8") as batch_log:
        for plan in plans:
            entry = entries_by_index.get(plan.index)
            if entry is None:
                continue
            if entry.get("batch_status") in TERMINAL_BATCH_STATUSES:
                logger.info(
                    "Skipping case %02d %s (%s); already %s.",
                    plan.index,
                    plan.spec.case_id,
                    plan.case_ref,
                    entry.get("batch_status"),
                )
                continue
            if runner.interrupted:
                break

            argv_for_case = _build_run_case_argv(args, plan.case_ref)
            started_at = _utc_now_iso()
            entry["started_at"] = started_at
            entry["batch_status"] = "running"
            summary["updated_at"] = _utc_now_iso()
            summary["status"] = "running"
            summary["totals"] = _summarize_cases(case_entries)
            _write_json(summary_path, summary)

            logger.info(
                "Running case %02d/%d: %s (%s)",
                plan.index,
                len(plans),
                plan.spec.case_id,
                plan.case_ref,
            )
            _append_log(
                batch_log,
                f"START case {plan.index:02d} {plan.spec.case_id} {started_at}",
                " ".join(argv_for_case),
            )

            before_dirs = _snapshot_run_dirs(plan.spec.case_dir)
            completed = runner.run_case_subprocess(argv_for_case)
            interrupted = runner.interrupted
            batch_status = _batch_status_for_exit(completed.returncode, interrupted=interrupted)
            finished_at = _utc_now_iso()

            case_logs_dir.mkdir(parents=True, exist_ok=True)
            stdout_path = case_logs_dir / f"{plan.index:02d}_{plan.spec.case_id}.stdout.log"
            stderr_path = case_logs_dir / f"{plan.index:02d}_{plan.spec.case_id}.stderr.log"
            stdout_path.write_text(completed.stdout or "", encoding="utf-8")
            stderr_path.write_text(completed.stderr or "", encoding="utf-8")
            _append_log(batch_log, f"STDOUT case {plan.index:02d}", completed.stdout or "")
            _append_log(batch_log, f"STDERR case {plan.index:02d}", completed.stderr or "")

            summary_path_obj, summary_payload = _resolve_run_summary(
                plan.spec.case_dir, before_dirs
            )
            run_status = None
            message = None
            compile_error = None
            duration_seconds = None
            artifact_dir = None
            if summary_payload is not None:
                run_status = summary_payload.get("status")
                message = summary_payload.get("message")
                compile_error = summary_payload.get("compile_error")
                duration_value = summary_payload.get("duration_seconds")
                if isinstance(duration_value, (int, float)):
                    duration_seconds = float(duration_value)
                artifact_value = summary_payload.get("artifact_dir")
                if isinstance(artifact_value, str):
                    artifact_dir = artifact_value

            outcome = CaseRunOutcome(
                batch_status=batch_status,
                exit_code=completed.returncode,
                run_summary_path=(
                    _relative_repo(summary_path_obj, args.repo_root) if summary_path_obj else None
                ),
                artifact_dir=artifact_dir,
                run_status=str(run_status) if run_status is not None else None,
                message=str(message) if message is not None else None,
                compile_error=str(compile_error) if compile_error is not None else None,
                duration_seconds=duration_seconds,
                started_at=started_at,
                finished_at=finished_at,
                stdout_path=_relative_repo(stdout_path, args.repo_root),
                stderr_path=_relative_repo(stderr_path, args.repo_root),
            )
            entry.update(_case_entry_from_outcome(plan, outcome))

            summary["updated_at"] = finished_at
            summary["totals"] = _summarize_cases(case_entries)
            _write_json(summary_path, summary)

            logger.info(
                "Finished case %02d %s: exit=%s batch_status=%s run_status=%s",
                plan.index,
                plan.spec.case_id,
                completed.returncode,
                batch_status,
                run_status,
            )
            _append_log(
                batch_log,
                f"END case {plan.index:02d} {plan.spec.case_id} exit={completed.returncode} "
                f"batch_status={batch_status} finished_at={finished_at}",
                "",
            )

            if runner.interrupted:
                break
            if args.stop_on_error and completed.returncode not in (0, None):
                logger.warning("Stopping batch after case %02d failure.", plan.index)
                break

            delay = max(0.0, args.delay_seconds)
            if batch_status in {"failed", "agent_ok_compile_fail"}:
                delay += max(0.0, args.delay_on_failure)
            if delay > 0 and not runner.interrupted:
                logger.info("Waiting %.1f seconds before next case.", delay)
                time.sleep(delay)

    summary["status"] = _batch_overall_status(case_entries, interrupted=runner.interrupted)
    summary["updated_at"] = _utc_now_iso()
    summary["totals"] = _summarize_cases(case_entries)
    _write_json(summary_path, summary)

    totals = summary["totals"]
    logger.info(
        "Batch %s finished with status=%s success=%s failed=%s compile_fail=%s interrupted=%s",
        args.batch_id,
        summary["status"],
        totals.get("success"),
        totals.get("failed"),
        totals.get("agent_ok_compile_fail"),
        totals.get("interrupted"),
    )
    print(json.dumps(summary, indent=2))

    if runner.interrupted:
        return 130
    if totals.get("success") == totals.get("planned"):
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
