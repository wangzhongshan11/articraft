"""Analyze turn statistics from record provenance metadata."""

from __future__ import annotations

import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path


def percentile(values: list[int], p: float) -> int:
    if not values:
        return 0
    sorted_values = sorted(values)
    idx = int(math.ceil(p / 100 * len(sorted_values))) - 1
    return sorted_values[max(0, min(idx, len(sorted_values) - 1))]


def main() -> None:
    records_dir = Path("data/records")
    rows: list[dict] = []
    missing = 0

    for rec_dir in sorted(records_dir.iterdir()):
        if not rec_dir.is_dir():
            continue
        prov_path = rec_dir / "revisions" / "rev_000001" / "provenance.json"
        if not prov_path.exists():
            missing += 1
            continue
        try:
            prov = json.loads(prov_path.read_text(encoding="utf-8"))
        except Exception:
            missing += 1
            continue
        gen = prov.get("generation") or {}
        rs = prov.get("run_summary") or {}
        rows.append(
            {
                "record_id": prov.get("record_id") or rec_dir.name,
                "provider": gen.get("provider"),
                "model_id": gen.get("model_id"),
                "thinking_level": gen.get("thinking_level"),
                "max_turns": gen.get("max_turns"),
                "turn_count": rs.get("turn_count"),
                "tool_call_count": rs.get("tool_call_count"),
                "compile_attempt_count": rs.get("compile_attempt_count"),
                "final_status": rs.get("final_status"),
            }
        )

    valid = [r for r in rows if isinstance(r["turn_count"], int) and r["turn_count"] > 0]
    agent_runs = valid
    turns = [r["turn_count"] for r in agent_runs]

    print("=== OVERVIEW ===")
    print(f"total_records={len(rows)} missing_provenance={missing}")
    print(f"agent_runs_with_turns={len(agent_runs)}")

    print("\n=== TURN COUNT ===")
    print(
        f"min={min(turns)} median={statistics.median(turns):.1f} "
        f"mean={statistics.mean(turns):.2f} max={max(turns)} "
        f"stdev={statistics.stdev(turns):.2f}"
    )
    for p in (10, 25, 50, 75, 90, 95, 99):
        print(f"p{p}={percentile(turns, p)}")

    buckets = Counter()
    for turn in turns:
        if turn <= 5:
            buckets["1-5"] += 1
        elif turn <= 10:
            buckets["6-10"] += 1
        elif turn <= 15:
            buckets["11-15"] += 1
        elif turn <= 20:
            buckets["16-20"] += 1
        elif turn <= 30:
            buckets["21-30"] += 1
        elif turn <= 50:
            buckets["31-50"] += 1
        else:
            buckets["51+"] += 1
    print("histogram:", dict(buckets))

    print("\n=== FINAL STATUS ===")
    status_counts = Counter(r["final_status"] for r in agent_runs)
    for status, count in status_counts.most_common():
        vals = [r["turn_count"] for r in agent_runs if r["final_status"] == status]
        print(
            f"{status}: n={count} median={statistics.median(vals):.1f} "
            f"mean={statistics.mean(vals):.2f}"
        )

    print("\n=== TOOL CALLS ===")
    tool_rows = [r for r in agent_runs if isinstance(r["tool_call_count"], int)]
    tool_counts = [r["tool_call_count"] for r in tool_rows]
    print(
        f"n={len(tool_counts)} min={min(tool_counts)} median={statistics.median(tool_counts):.1f} "
        f"mean={statistics.mean(tool_counts):.2f} max={max(tool_counts)}"
    )
    ratios = [r["tool_call_count"] / r["turn_count"] for r in tool_rows if r["turn_count"] > 0]
    print(
        f"tool_calls_per_turn: median={statistics.median(ratios):.3f} "
        f"mean={statistics.mean(ratios):.3f}"
    )
    diff = [r["tool_call_count"] - r["turn_count"] for r in tool_rows]
    print(
        f"tool_minus_turn: median={statistics.median(diff):.1f} "
        f"mean={statistics.mean(diff):.2f} min={min(diff)} max={max(diff)}"
    )

    print("\n=== COMPILE ATTEMPTS (fix cycles proxy) ===")
    compile_rows = [r for r in agent_runs if isinstance(r["compile_attempt_count"], int)]
    compile_counts = [r["compile_attempt_count"] for r in compile_rows]
    print(
        f"n={len(compile_counts)} min={min(compile_counts)} "
        f"median={statistics.median(compile_counts):.1f} "
        f"mean={statistics.mean(compile_counts):.2f} max={max(compile_counts)}"
    )
    compile_ratios = [
        r["compile_attempt_count"] / r["turn_count"] for r in compile_rows if r["turn_count"] > 0
    ]
    print(
        f"compile_attempts_per_turn: median={statistics.median(compile_ratios):.3f} "
        f"mean={statistics.mean(compile_ratios):.3f}"
    )

    success_rows = [r for r in compile_rows if r["final_status"] == "success"]
    fail_rows = [r for r in compile_rows if r["final_status"] != "success"]
    if success_rows:
        s = [r["compile_attempt_count"] for r in success_rows]
        print(
            f"success compile_attempts: n={len(s)} median={statistics.median(s):.1f} "
            f"mean={statistics.mean(s):.2f}"
        )
    if fail_rows:
        f = [r["compile_attempt_count"] for r in fail_rows]
        print(
            f"non-success compile_attempts: n={len(f)} median={statistics.median(f):.1f} "
            f"mean={statistics.mean(f):.2f}"
        )

    compile_hist = Counter()
    for count in compile_counts:
        if count == 1:
            compile_hist["1 (first try)"] += 1
        elif count <= 3:
            compile_hist["2-3"] += 1
        elif count <= 5:
            compile_hist["4-5"] += 1
        elif count <= 10:
            compile_hist["6-10"] += 1
        else:
            compile_hist["11+"] += 1
    print("compile_histogram:", dict(compile_hist))

    print("\n=== BY PROVIDER ===")
    by_provider: dict[str, list[int]] = defaultdict(list)
    for row in agent_runs:
        by_provider[row.get("provider") or "unknown"].append(row["turn_count"])
    for provider in sorted(by_provider):
        vals = by_provider[provider]
        print(
            f"{provider}: n={len(vals)} median={statistics.median(vals):.1f} "
            f"mean={statistics.mean(vals):.2f}"
        )

    print("\n=== BY MODEL (top 8) ===")
    by_model: dict[str, list[int]] = defaultdict(list)
    for row in agent_runs:
        by_model[row.get("model_id") or "unknown"].append(row["turn_count"])
    for model_id, vals in sorted(by_model.items(), key=lambda item: -len(item[1]))[:8]:
        print(
            f"{model_id}: n={len(vals)} median={statistics.median(vals):.1f} "
            f"mean={statistics.mean(vals):.2f}"
        )

    print("\n=== MAX TURNS ===")
    max_turn_vals = Counter(r.get("max_turns") for r in agent_runs)
    print("configured max_turns:", dict(max_turn_vals.most_common()))
    hit_limit = [
        r
        for r in agent_runs
        if isinstance(r["max_turns"], int) and r["turn_count"] >= r["max_turns"]
    ]
    print(f"hit_max_turns (turn_count >= max_turns): n={len(hit_limit)}")
    hit_status = [r for r in agent_runs if r["final_status"] == "max_turns"]
    print(f"final_status=max_turns: n={len(hit_status)}")

    print("\n=== NON-AGENT / ZERO TURN ===")
    zero_or_missing = [r for r in rows if not isinstance(r["turn_count"], int) or r["turn_count"] == 0]
    print(f"n={len(zero_or_missing)} statuses={dict(Counter(r['final_status'] for r in zero_or_missing))}")

    print("\n=== TOP 10 LONGEST RUNS ===")
    for row in sorted(agent_runs, key=lambda item: item["turn_count"], reverse=True)[:10]:
        print(
            f"{row['record_id']}: turns={row['turn_count']} tools={row['tool_call_count']} "
            f"compile={row['compile_attempt_count']} status={row['final_status']}"
        )


if __name__ == "__main__":
    main()
