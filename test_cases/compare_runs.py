"""
Compare two benchmark run_summary.json files for OneAPI A/B analysis.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

COMPARE_KEYS = (
    "status",
    "failure_kind",
    "model_id",
    "openai_api",
    "openai_transport",
    "compaction_mode",
    "thinking_level",
    "turn_count",
    "tool_call_count",
    "compile_attempt_count",
    "total_tokens",
    "cached_tokens",
    "prompt_tokens",
    "total_cost_usd",
    "duration_seconds",
)


def _load_summary(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object JSON in {path}")
    return payload


def _format_value(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _compare(left: dict[str, Any], right: dict[str, Any]) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for key in COMPARE_KEYS:
        left_value = left.get(key)
        right_value = right.get(key)
        if left_value == right_value and left_value is None:
            continue
        rows.append((key, _format_value(left_value), _format_value(right_value)))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare two run_summary.json files (OneAPI A/B metrics)."
    )
    parser.add_argument("left", type=Path, help="Path to run_summary.json (baseline)")
    parser.add_argument("right", type=Path, help="Path to run_summary.json (candidate)")
    args = parser.parse_args(argv)

    try:
        left_summary = _load_summary(args.left.resolve())
        right_summary = _load_summary(args.right.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    rows = _compare(left_summary, right_summary)
    label_left = str(left_summary.get("artifact_dir") or args.left)
    label_right = str(right_summary.get("artifact_dir") or args.right)
    print(f"{'metric':<24} {label_left:<36} {label_right}")
    print("-" * 100)
    for key, left_value, right_value in rows:
        print(f"{key:<24} {left_value:<36} {right_value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
