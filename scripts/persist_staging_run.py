"""Recover a successful staging run into data/records/."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from agent.prompts import resolve_system_prompt_path
from agent.record_persistence import SuccessRecordWrite, write_success_record
from agent.run_context import _build_single_run_context
from storage.collections import CollectionStore
from storage.datasets import DatasetStore
from storage.records import RecordStore
from storage.repo import StorageRepo


def persist_staging_run(*, repo_root: Path, run_id: str) -> Path:
    run_dir = repo_root / "data" / "cache" / "runs" / run_id
    results = json.loads(run_dir.joinpath("results.jsonl").read_text(encoding="utf-8").strip())
    run_meta = json.loads(run_dir.joinpath("run.json").read_text(encoding="utf-8"))
    record_id = results["record_id"]
    staging_dir = repo_root / results["staging_dir"]
    settings = run_meta["settings_summary"]

    prompt_text = (staging_dir / "prompt.txt").read_text(encoding="utf-8")
    final_code = (staging_dir / "model.py").read_text(encoding="utf-8")
    urdf_xml = (staging_dir / "model.urdf").read_text(encoding="utf-8")

    storage_repo = StorageRepo(repo_root)
    storage_repo.ensure_layout()
    created_at = datetime.fromisoformat(run_meta["created_at"].replace("Z", "+00:00"))
    context = _build_single_run_context(
        repo_root=repo_root,
        prompt=prompt_text,
        storage_repo=storage_repo,
        record_id=record_id,
        run_id=run_id,
        now=created_at,
    )
    if context.staging_dir.resolve() != staging_dir.resolve():
        raise ValueError(
            f"Staging dir mismatch: expected {staging_dir}, got {context.staging_dir}"
        )

    record_store = RecordStore(storage_repo)
    collections = CollectionStore(storage_repo)
    datasets = DatasetStore(storage_repo)
    system_prompt_path = resolve_system_prompt_path(
        settings["system_prompt_path"],
        provider=run_meta["provider"],
        sdk_package=run_meta["sdk_package"],
        repo_root=repo_root,
    )

    return write_success_record(
        SuccessRecordWrite(
            repo_root=repo_root,
            storage_repo=storage_repo,
            record_store=record_store,
            collections=collections,
            datasets=datasets,
            context=context,
            prompt_text=prompt_text,
            display_prompt=prompt_text,
            image_path=None,
            provider=run_meta["provider"],
            model_id=run_meta["model_id"],
            openai_transport=settings.get("openai_transport", "http"),
            openai_api=settings.get("openai_api", "responses"),
            thinking_level=settings["thinking_level"],
            max_turns=settings["max_turns"],
            system_prompt_path=system_prompt_path,
            sdk_package=run_meta["sdk_package"],
            openai_reasoning_summary=settings.get("openai_reasoning_summary"),
            max_cost_usd=settings.get("max_cost_usd"),
            final_code=final_code,
            urdf_xml=urdf_xml,
            compile_warnings=[],
            turn_count=results["turn_count"],
            tool_call_count=results["tool_call_count"],
            compile_attempt_count=results["compile_attempt_count"],
            label=None,
            tags=[],
            collection=run_meta["collection"],
            category_slug=None,
            dataset_id=None,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist a successful staging run.")
    parser.add_argument("run_id", help="Run id under data/cache/runs/, e.g. run_20260703_...")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Articraft repo root",
    )
    args = parser.parse_args()
    record_dir = persist_staging_run(repo_root=args.repo_root.resolve(), run_id=args.run_id)
    print(record_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
