#!/usr/bin/env python3
"""
Enumerate project documentation Markdown files and report paths for _c translation.

Naming rule: README.md -> README_c.md (insert _c before extension)

Excluded: data/categories, data/records, data/system_prompts, data/cache,
          .venv, node_modules, agent/prompts/generated (compiled LLM prompts)
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_DIR_PARTS = (
    "data/categories",
    "data/records",
    "data/system_prompts",
    "data/cache",
    ".venv",
    "node_modules",
    "agent/prompts/generated",
)

INCLUDE_ROOT_FILES = (
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "EXTERNAL_AGENT_DATA.md",
    "SECURITY.md",
)

INCLUDE_PREFIXES = (
    "docs/",
    "data/CATEGORY",
    "data/REJECTED",
    ".github/",
    "agent/prompts/sections/",
    "sdk/_docs/",
    "sdk/_examples/",
)


def is_doc_path(rel: str) -> bool:
    if not rel.endswith(".md"):
        return False
    if rel.endswith("_c.md"):
        return False
    normalized = rel.replace("\\", "/")
    for part in EXCLUDE_DIR_PARTS:
        if part in normalized:
            return False
    if normalized in INCLUDE_ROOT_FILES:
        return True
    return any(normalized.startswith(p) for p in INCLUDE_PREFIXES)


def target_path(source: Path) -> Path:
    return source.with_name(f"{source.stem}_c{source.suffix}")


def collect_docs() -> list[Path]:
    found: list[Path] = []
    for path in REPO_ROOT.rglob("*.md"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if is_doc_path(rel):
            found.append(path)
    return sorted(found, key=lambda p: p.as_posix())


def main() -> int:
    parser = argparse.ArgumentParser(description="List doc paths and _c targets")
    parser.add_argument("--missing-only", action="store_true")
    args = parser.parse_args()
    docs = collect_docs()
    missing = [p for p in docs if not target_path(p).exists()]
    print(f"Total documentation files: {len(docs)}")
    print(f"Missing _c translations: {len(missing)}")
    for path in missing if args.missing_only else docs:
        rel = path.relative_to(REPO_ROOT)
        tgt = target_path(path).relative_to(REPO_ROOT)
        print(f"{rel} -> {tgt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
