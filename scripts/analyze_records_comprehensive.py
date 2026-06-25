"""Comprehensive analysis of all records under data/records."""

from __future__ import annotations

import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    idx = int(math.ceil(p / 100 * len(sorted_values))) - 1
    return sorted_values[max(0, min(idx, len(sorted_values) - 1))]


def parse_ts(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def stats(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "min": min(values),
        "p10": percentile(values, 10),
        "p25": percentile(values, 25),
        "median": statistics.median(values),
        "mean": statistics.mean(values),
        "p75": percentile(values, 75),
        "p90": percentile(values, 90),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def fmt_stats(label: str, s: dict[str, float | int], unit: str = "") -> str:
    if s.get("n", 0) == 0:
        return f"{label}: n=0"
    suffix = f" {unit}".rstrip()
    return (
        f"{label}: n={int(s['n'])} min={s['min']:.2f}{suffix} "
        f"p50={s['median']:.2f}{suffix} mean={s['mean']:.2f}{suffix} "
        f"p90={s['p90']:.2f}{suffix} p95={s['p95']:.2f}{suffix} "
        f"max={s['max']:.2f}{suffix}"
    )


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def main() -> None:
    records_dir = Path("data/records")
    cache_dir = Path("data/cache/record_materialization")
    rows: list[dict[str, Any]] = []
    errors = Counter()

    for rec_dir in sorted(records_dir.iterdir()):
        if not rec_dir.is_dir():
            continue
        record_id = rec_dir.name
        record = load_json(rec_dir / "record.json")
        if record is None:
            errors["missing_record_json"] += 1
            continue

        rev_id = record.get("active_revision_id") or "rev_000001"
        rev_dir = rec_dir / "revisions" / rev_id
        prov = load_json(rev_dir / "provenance.json")
        cost = load_json(rev_dir / "cost.json")
        compile_report = load_json(cache_dir / record_id / "compile_report.json")

        created_at = parse_ts(record.get("created_at"))
        updated_at = parse_ts(record.get("updated_at"))
        wall_seconds: float | None = None
        if created_at and updated_at:
            wall_seconds = max(0.0, (updated_at - created_at).total_seconds())

        gen = (prov or {}).get("generation") or {}
        rs = (prov or {}).get("run_summary") or {}
        cost_total = ((cost or {}).get("total") or {}).get("costs_usd") or {}
        cost_tokens = ((cost or {}).get("total") or {}).get("tokens") or {}
        metrics = (compile_report or {}).get("metrics") or {}

        turn_count = rs.get("turn_count")
        total_cost = cost_total.get("total")
        total_tokens = cost_tokens.get("total_tokens")
        compile_elapsed = metrics.get("compile_elapsed_seconds")

        cost_turns = cost.get("turns") if isinstance(cost, dict) else None
        cost_turn_count = len(cost_turns) if isinstance(cost_turns, list) else None

        rows.append(
            {
                "record_id": record_id,
                "kind": record.get("kind"),
                "category_slug": record.get("category_slug"),
                "rating": record.get("rating"),
                "author": record.get("author"),
                "provider": record.get("provider") or gen.get("provider"),
                "model_id": record.get("model_id") or gen.get("model_id"),
                "thinking_level": gen.get("thinking_level"),
                "max_turns": gen.get("max_turns"),
                "turn_count": turn_count,
                "tool_call_count": rs.get("tool_call_count"),
                "compile_attempt_count": rs.get("compile_attempt_count"),
                "final_status": rs.get("final_status"),
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at"),
                "wall_seconds": wall_seconds,
                "total_cost_usd": total_cost,
                "total_tokens": total_tokens,
                "cost_turn_count": cost_turn_count,
                "compile_elapsed_seconds": compile_elapsed,
                "has_cost": cost is not None,
                "has_provenance": prov is not None,
                "platform": ((prov or {}).get("environment") or {}).get("platform"),
                "batch_spec_id": (record.get("source") or {}).get("batch_spec_id"),
                "run_id": (record.get("source") or {}).get("run_id"),
            }
        )

    agent_rows = [
        r
        for r in rows
        if isinstance(r["turn_count"], int) and r["turn_count"] > 0 and r["final_status"] != "draft"
    ]
    cost_rows = [r for r in agent_rows if isinstance(r["total_cost_usd"], (int, float))]
    wall_rows = [r for r in agent_rows if isinstance(r["wall_seconds"], (int, float))]
    compile_rows = [
        r for r in agent_rows if isinstance(r["compile_elapsed_seconds"], (int, float))
    ]

    print("=" * 72)
    print("ARTICRAFT RECORDS — COMPREHENSIVE RUN ANALYSIS")
    print("=" * 72)

    print("\n## 1. DATASET OVERVIEW")
    print(f"total_record_dirs={len(rows)} parse_errors={dict(errors)}")
    print(f"agent_runs_with_turns={len(agent_rows)}")
    print(f"records_with_cost_json={len(cost_rows)}")
    print(f"records_with_wall_clock={len(wall_rows)}")
    print(f"records_with_compile_elapsed={len(compile_rows)}")

    kind_counts = Counter(r["kind"] for r in rows)
    status_counts = Counter(r["final_status"] for r in rows)
    print("kind:", dict(kind_counts.most_common()))
    print("final_status:", dict(status_counts.most_common(12)))

    zero_turn = [r for r in rows if not isinstance(r["turn_count"], int) or r["turn_count"] == 0]
    print(f"zero_or_missing_turns={len(zero_turn)}")
    if zero_turn:
        print("zero_turn_statuses:", dict(Counter(r["final_status"] for r in zero_turn)))

    print("\n## 2. TURN COUNT DISTRIBUTION")
    turns = [float(r["turn_count"]) for r in agent_rows]
    print(fmt_stats("turns", stats(turns)))
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

    print("\n## 3. WALL-CLOCK TIME PER CASE (updated_at - created_at)")
    print("NOTE: includes post-generation edits/ratings, not pure LLM runtime")
    walls = [float(r["wall_seconds"]) for r in wall_rows]
    s = stats(walls)
    print(fmt_stats("wall_seconds", s, "s"))
    print(fmt_stats("wall_minutes", stats([w / 60 for w in walls]), "min"))
    print(fmt_stats("wall_hours", stats([w / 3600 for w in walls]), "h"))

    if walls and turns:
        paired = [
            (r["wall_seconds"], r["turn_count"])
            for r in wall_rows
            if isinstance(r["turn_count"], int) and r["turn_count"] > 0
        ]
        sec_per_turn = [w / t for w, t in paired if t > 0]
        print(fmt_stats("wall_seconds_per_turn", stats(sec_per_turn), "s/turn"))

    print("\n## 4. COST PER CASE (cost.json total)")
    costs = [float(r["total_cost_usd"]) for r in cost_rows]
    print(fmt_stats("total_cost_usd", stats(costs), "USD"))
    tokens = [float(r["total_tokens"]) for r in cost_rows if isinstance(r["total_tokens"], (int, float))]
    print(fmt_stats("total_tokens", stats(tokens)))

    paired_cost_turn = [
        (float(r["total_cost_usd"]), int(r["turn_count"]))
        for r in cost_rows
        if isinstance(r["turn_count"], int) and r["turn_count"] > 0
    ]
    if paired_cost_turn:
        cost_per_turn = [c / t for c, t in paired_cost_turn]
        print(fmt_stats("cost_usd_per_turn", stats(cost_per_turn), "USD/turn"))

    paired_cost_wall = [
        (float(r["total_cost_usd"]), float(r["wall_seconds"]))
        for r in cost_rows
        if isinstance(r["wall_seconds"], (int, float)) and r["wall_seconds"] > 0
    ]
    if paired_cost_wall:
        cost_per_min = [c / (w / 60) for c, w in paired_cost_wall]
        print(fmt_stats("cost_usd_per_wall_minute", stats(cost_per_min), "USD/min"))

    print("\n## 5. COMPILE TIME (materialization cache)")
    compile_secs = [float(r["compile_elapsed_seconds"]) for r in compile_rows]
    print(fmt_stats("compile_elapsed_seconds", stats(compile_secs), "s"))

    print("\n## 6. TOOL CALLS & COMPILE ATTEMPTS")
    tool_rows = [r for r in agent_rows if isinstance(r["tool_call_count"], int)]
    tools = [float(r["tool_call_count"]) for r in tool_rows]
    print(fmt_stats("tool_call_count", stats(tools)))
    ratios = [
        r["tool_call_count"] / r["turn_count"]
        for r in tool_rows
        if isinstance(r["turn_count"], int) and r["turn_count"] > 0
    ]
    print(fmt_stats("tool_calls_per_turn", stats(ratios)))

    compile_attempt_rows = [r for r in agent_rows if isinstance(r["compile_attempt_count"], int)]
    compile_attempts = [float(r["compile_attempt_count"]) for r in compile_attempt_rows]
    print(fmt_stats("compile_attempt_count", stats(compile_attempts)))
    compile_ratios = [
        r["compile_attempt_count"] / r["turn_count"]
        for r in compile_attempt_rows
        if isinstance(r["turn_count"], int) and r["turn_count"] > 0
    ]
    print(fmt_stats("compile_attempts_per_turn", stats(compile_ratios)))

    print("\n## 7. BY PROVIDER")
    by_provider: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in agent_rows:
        by_provider[row.get("provider") or "unknown"].append(row)
    for provider in sorted(by_provider, key=lambda k: -len(by_provider[k])):
        group = by_provider[provider]
        t = [float(r["turn_count"]) for r in group]
        c = [float(r["total_cost_usd"]) for r in group if isinstance(r["total_cost_usd"], (int, float))]
        w = [float(r["wall_seconds"]) for r in group if isinstance(r["wall_seconds"], (int, float))]
        print(
            f"{provider}: n={len(group)} turns_mean={statistics.mean(t):.2f} "
            f"cost_mean={statistics.mean(c):.4f} USD" if c else f"{provider}: n={len(group)} turns_mean={statistics.mean(t):.2f}",
            end="",
        )
        if w:
            print(f" wall_mean={statistics.mean(w)/60:.1f} min", end="")
        print()

    print("\n## 8. BY MODEL")
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in agent_rows:
        by_model[row.get("model_id") or "unknown"].append(row)
    for model_id, group in sorted(by_model.items(), key=lambda item: -len(item[1])):
        t = [float(r["turn_count"]) for r in group]
        c = [float(r["total_cost_usd"]) for r in group if isinstance(r["total_cost_usd"], (int, float))]
        w = [float(r["wall_seconds"]) for r in group if isinstance(r["wall_seconds"], (int, float))]
        line = (
            f"{model_id}: n={len(group)} turns_p50={statistics.median(t):.0f} "
            f"turns_mean={statistics.mean(t):.2f}"
        )
        if c:
            line += f" cost_mean=${statistics.mean(c):.4f}"
        if w:
            line += f" wall_mean={statistics.mean(w)/60:.1f}min"
        print(line)

    print("\n## 9. BY THINKING LEVEL")
    by_thinking: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in agent_rows:
        by_thinking[row.get("thinking_level") or "unknown"].append(row)
    for level, group in sorted(by_thinking.items(), key=lambda item: -len(item[1])):
        t = [float(r["turn_count"]) for r in group]
        c = [float(r["total_cost_usd"]) for r in group if isinstance(r["total_cost_usd"], (int, float))]
        print(
            f"{level}: n={len(group)} turns_mean={statistics.mean(t):.2f}"
            + (f" cost_mean=${statistics.mean(c):.4f}" if c else "")
        )

    print("\n## 10. BY CATEGORY (top 20 by count)")
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in agent_rows:
        by_category[row.get("category_slug") or "(uncategorized)"].append(row)
    for slug, group in sorted(by_category.items(), key=lambda item: -len(item[1]))[:20]:
        t = [float(r["turn_count"]) for r in group]
        c = [float(r["total_cost_usd"]) for r in group if isinstance(r["total_cost_usd"], (int, float))]
        w = [float(r["wall_seconds"]) for r in group if isinstance(r["wall_seconds"], (int, float))]
        line = (
            f"{slug}: n={len(group)} turns_mean={statistics.mean(t):.1f} "
            f"turns_p90={percentile(t, 90):.0f}"
        )
        if c:
            line += f" cost_mean=${statistics.mean(c):.3f}"
        if w:
            line += f" wall_mean={statistics.mean(w)/60:.0f}min"
        print(line)

    print("\n## 11. BY RATING")
    by_rating: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in agent_rows:
        rating = row.get("rating")
        key = str(rating) if rating is not None else "unrated"
        by_rating[key].append(row)
    for rating in sorted(by_rating, key=lambda k: (k == "unrated", k)):
        group = by_rating[rating]
        t = [float(r["turn_count"]) for r in group]
        c = [float(r["total_cost_usd"]) for r in group if isinstance(r["total_cost_usd"], (int, float))]
        print(
            f"rating={rating}: n={len(group)} turns_mean={statistics.mean(t):.1f}"
            + (f" cost_mean=${statistics.mean(c):.3f}" if c else "")
        )

    print("\n## 12. MAX TURNS CONFIG vs ACTUAL")
    hit_limit = [
        r
        for r in agent_rows
        if isinstance(r["max_turns"], int) and isinstance(r["turn_count"], int) and r["turn_count"] >= r["max_turns"]
    ]
    print(f"hit_or_exceeded_configured_max_turns: n={len(hit_limit)}")
    print("configured max_turns top:", dict(Counter(r.get("max_turns") for r in agent_rows).most_common(10)))

    print("\n## 13. OUTLIERS — LONGEST BY TURNS")
    for row in sorted(agent_rows, key=lambda r: r["turn_count"], reverse=True)[:15]:
        wall = row["wall_seconds"]
        wall_s = f"{wall/60:.0f}min" if isinstance(wall, (int, float)) else "?"
        cost = row["total_cost_usd"]
        cost_s = f"${cost:.3f}" if isinstance(cost, (int, float)) else "?"
        print(
            f"{row['record_id']}: turns={row['turn_count']} tools={row['tool_call_count']} "
            f"compile_attempts={row['compile_attempt_count']} cost={cost_s} wall={wall_s} "
            f"model={row['model_id']} category={row['category_slug']}"
        )

    print("\n## 14. OUTLIERS — MOST EXPENSIVE")
    for row in sorted(
        cost_rows,
        key=lambda r: float(r["total_cost_usd"]) if isinstance(r["total_cost_usd"], (int, float)) else 0,
        reverse=True,
    )[:15]:
        wall = row["wall_seconds"]
        wall_s = f"{wall/60:.0f}min" if isinstance(wall, (int, float)) else "?"
        print(
            f"{row['record_id']}: cost=${row['total_cost_usd']:.4f} turns={row['turn_count']} "
            f"tokens={row['total_tokens']} wall={wall_s} category={row['category_slug']}"
        )

    print("\n## 15. OUTLIERS — LONGEST WALL CLOCK")
    for row in sorted(
        wall_rows,
        key=lambda r: float(r["wall_seconds"]) if isinstance(r["wall_seconds"], (int, float)) else 0,
        reverse=True,
    )[:15]:
        wall = float(row["wall_seconds"])
        cost = row["total_cost_usd"]
        cost_s = f"${cost:.3f}" if isinstance(cost, (int, float)) else "?"
        print(
            f"{row['record_id']}: wall={wall/3600:.1f}h turns={row['turn_count']} cost={cost_s} "
            f"category={row['category_slug']} updated={row['updated_at']}"
        )

    print("\n## 16. MONTHLY GENERATION VOLUME")
    by_month: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in agent_rows:
        ts = row.get("created_at")
        if isinstance(ts, str) and len(ts) >= 7:
            by_month[ts[:7]].append(row)
    for month in sorted(by_month):
        group = by_month[month]
        t = [float(r["turn_count"]) for r in group]
        c = [float(r["total_cost_usd"]) for r in group if isinstance(r["total_cost_usd"], (int, float))]
        total_cost = sum(c) if c else 0.0
        print(
            f"{month}: n={len(group)} turns_mean={statistics.mean(t):.1f} "
            f"total_cost=${total_cost:,.0f} avg_cost=${statistics.mean(c):.3f}" if c else f"{month}: n={len(group)}"
        )

    print("\n## 17. AGGREGATE TOTALS")
    total_cost_sum = sum(float(r["total_cost_usd"]) for r in cost_rows)
    total_tokens_sum = sum(
        float(r["total_tokens"]) for r in cost_rows if isinstance(r["total_tokens"], (int, float))
    )
    total_turns_sum = sum(int(r["turn_count"]) for r in agent_rows)
    total_tool_sum = sum(
        int(r["tool_call_count"]) for r in agent_rows if isinstance(r["tool_call_count"], int)
    )
    total_compile_attempts = sum(
        int(r["compile_attempt_count"])
        for r in agent_rows
        if isinstance(r["compile_attempt_count"], int)
    )
    print(f"sum_turns={total_turns_sum:,}")
    print(f"sum_tool_calls={total_tool_sum:,}")
    print(f"sum_compile_attempts={total_compile_attempts:,}")
    print(f"sum_cost_usd=${total_cost_sum:,.2f}")
    print(f"sum_tokens={total_tokens_sum:,.0f}")
    if agent_rows:
        print(f"avg_turns_per_case={total_turns_sum/len(agent_rows):.2f}")
    if cost_rows:
        print(f"avg_cost_per_case=${total_cost_sum/len(cost_rows):.4f}")

    print("\n## 18. COST vs TURN MISMATCH")
    mismatches = [
        r
        for r in agent_rows
        if isinstance(r["cost_turn_count"], int)
        and isinstance(r["turn_count"], int)
        and r["cost_turn_count"] != r["turn_count"]
    ]
    print(f"records_where_cost_turns_len != provenance_turn_count: n={len(mismatches)}")
    if mismatches:
        diffs = [r["cost_turn_count"] - r["turn_count"] for r in mismatches]
        print(
            f"mismatch_diff: min={min(diffs)} median={statistics.median(diffs):.0f} "
            f"max={max(diffs)}"
        )


if __name__ == "__main__":
    main()
