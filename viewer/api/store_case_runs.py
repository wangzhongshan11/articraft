from __future__ import annotations

from pathlib import Path
from typing import Any

from viewer.api.schemas import CaseRunEntryResponse
from viewer.api.store_components import ViewerStoreComponent
from viewer.api.store_filesystem import (
    _file_mtime_to_utc,
    _first_nonempty_line,
    _mtime_to_utc,
    _truncate_text,
)
from viewer.api.store_values import (
    _coerce_float,
    _coerce_int,
    _coerce_string,
    _relative_path,
)


def _latest_artifact_timestamp(artifact_dir: Path, fallback: str | None) -> str | None:
    candidates = (
        artifact_dir,
        artifact_dir / "prompt.txt",
        artifact_dir / "model.py",
        artifact_dir / "model.urdf",
        artifact_dir / "cost.json",
        artifact_dir / "compile_report.json",
        artifact_dir / "run_summary.json",
        artifact_dir / "assets",
        artifact_dir / "assets" / "meshes",
        artifact_dir / "assets" / "glb",
        artifact_dir / "assets" / "viewer",
        artifact_dir / "traces",
        artifact_dir / "traces" / "trajectory.jsonl",
    )
    latest_mtime: float | None = None
    for candidate in candidates:
        try:
            stat = candidate.stat()
        except OSError:
            continue
        if latest_mtime is None or stat.st_mtime > latest_mtime:
            latest_mtime = stat.st_mtime
    if latest_mtime is None:
        return fallback
    return _mtime_to_utc(latest_mtime)


def _suite_from_case_dir(case_dir: Path, test_cases_root: Path) -> str | None:
    try:
        relative = case_dir.resolve().relative_to(test_cases_root.resolve())
    except ValueError:
        return None
    parts = relative.parts
    if not parts:
        return None
    if parts[0] == "cases":
        return "cases"
    return parts[0]


def _case_id_from_summary(summary: dict[str, Any] | None, case_dir: Path) -> str:
    if isinstance(summary, dict):
        case_id = _coerce_string(summary.get("case_id"))
        if case_id:
            return case_id
    return case_dir.name


class ViewerCaseRunsStore(ViewerStoreComponent):
    def test_cases_root(self) -> Path:
        return (self.repo_root / "test_cases").resolve()

    @staticmethod
    def _directory_has_files(path: Path) -> bool:
        if not path.is_dir():
            return False
        try:
            return any(path.iterdir())
        except OSError:
            return False

    def list_case_run_entries(self) -> list[CaseRunEntryResponse]:
        test_cases_root = self.test_cases_root()
        if not test_cases_root.is_dir():
            return []

        entries: list[CaseRunEntryResponse] = []
        for runs_dir in test_cases_root.rglob("runs"):
            if not runs_dir.is_dir():
                continue
            case_dir = runs_dir.parent
            for run_dir in sorted(path for path in runs_dir.iterdir() if path.is_dir()):
                entry = self._case_run_entry_from_dir(
                    run_dir,
                    case_dir=case_dir,
                    test_cases_root=test_cases_root,
                )
                if entry is not None:
                    entries.append(entry)

        entries.sort(
            key=lambda item: item.updated_at or item.run_token,
            reverse=True,
        )
        return entries

    def _case_run_entry_from_dir(
        self,
        run_dir: Path,
        *,
        case_dir: Path,
        test_cases_root: Path,
    ) -> CaseRunEntryResponse | None:
        summary_path = run_dir / "run_summary.json"
        summary = self.repo.read_json(summary_path)
        if summary is not None and not isinstance(summary, dict):
            summary = None

        prompt_path = run_dir / "prompt.txt"
        model_script_path = run_dir / "model.py"
        checkpoint_urdf_path = run_dir / "model.urdf"
        cost_path = run_dir / "cost.json"
        traces_dir = run_dir / "traces"

        prompt_text = self.records._read_text(prompt_path)
        prompt_preview = ""
        if prompt_text:
            prompt_preview = _truncate_text(prompt_text)
        elif isinstance(summary, dict):
            preview = _coerce_string(summary.get("message"))
            if preview:
                prompt_preview = _truncate_text(preview)

        case_id = _case_id_from_summary(summary if isinstance(summary, dict) else None, case_dir)
        suite = (
            _coerce_string(summary.get("suite")) if isinstance(summary, dict) else None
        ) or _suite_from_case_dir(case_dir, test_cases_root)
        run_token = run_dir.name
        title = (
            _first_nonempty_line(prompt_text)
            if prompt_text
            else (_coerce_string(summary.get("case_id")) if isinstance(summary, dict) else None)
            or case_id
        )

        updated_at = _latest_artifact_timestamp(
            run_dir,
            _coerce_string(summary.get("artifact_dir")) if isinstance(summary, dict) else None,
        )

        return CaseRunEntryResponse(
            case_run_path=_relative_path(run_dir, self.repo_root),
            case_id=case_id,
            suite=suite,
            case_dir=_relative_path(case_dir, self.repo_root),
            run_token=run_token,
            title=title,
            prompt_preview=prompt_preview,
            status=_coerce_string(summary.get("status")) if isinstance(summary, dict) else None,
            message=_coerce_string(summary.get("message")) if isinstance(summary, dict) else None,
            provider=_coerce_string(summary.get("provider")) if isinstance(summary, dict) else None,
            model_id=_coerce_string(summary.get("model_id")) if isinstance(summary, dict) else None,
            thinking_level=(
                _coerce_string(summary.get("thinking_level")) if isinstance(summary, dict) else None
            ),
            turn_count=(
                _coerce_int(summary.get("turn_count")) if isinstance(summary, dict) else None
            ),
            tool_call_count=(
                _coerce_int(summary.get("tool_call_count")) if isinstance(summary, dict) else None
            ),
            compile_attempt_count=(
                _coerce_int(summary.get("compile_attempt_count"))
                if isinstance(summary, dict)
                else None
            ),
            total_cost_usd=(
                _coerce_float(summary.get("total_cost_usd")) if isinstance(summary, dict) else None
            ),
            run_id=_coerce_string(summary.get("run_id")) if isinstance(summary, dict) else None,
            record_id=_coerce_string(summary.get("record_id"))
            if isinstance(summary, dict)
            else None,
            updated_at=updated_at,
            has_prompt=prompt_path.is_file(),
            has_model_script=model_script_path.is_file(),
            model_script_updated_at=_file_mtime_to_utc(model_script_path),
            has_checkpoint_urdf=checkpoint_urdf_path.is_file(),
            checkpoint_updated_at=_file_mtime_to_utc(checkpoint_urdf_path),
            has_cost=cost_path.is_file(),
            has_traces=self._directory_has_files(traces_dir),
            has_compile_report=(run_dir / "compile_report.json").is_file(),
            prompt_file=(
                _coerce_string(summary.get("prompt_file")) if isinstance(summary, dict) else None
            ),
            reference_image=(
                _coerce_string(summary.get("reference_image"))
                if isinstance(summary, dict)
                else None
            ),
            compile_target=(
                _coerce_string(summary.get("compile_target")) if isinstance(summary, dict) else None
            ),
            compile_error=(
                _coerce_string(summary.get("compile_error")) if isinstance(summary, dict) else None
            ),
        )

    def read_run_summary(self, artifact_dir: Path) -> dict[str, Any] | None:
        payload = self.repo.read_json(artifact_dir / "run_summary.json")
        return payload if isinstance(payload, dict) else None

    def read_compile_report(self, artifact_dir: Path) -> dict[str, Any] | None:
        payload = self.repo.read_json(artifact_dir / "compile_report.json")
        return payload if isinstance(payload, dict) else None
