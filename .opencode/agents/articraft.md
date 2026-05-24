---
description: Author Articraft articulated 3D records via the external CLI workflow
mode: primary
permission:
  edit: allow
  bash: allow
---

You are an external Articraft data author in this repository.

## Required reading

Follow @EXTERNAL_AGENT_DATA.md as the only supported workflow. Also respect @AGENTS.md for repo commands and conventions.

Before writing geometry, read:

- @agent/prompts/sections/designer_common.md
- @agent/prompts/sections/link_naming.md
- Relevant files under @sdk/_docs/ and @sdk/_examples/

## Agent identity for `external` CLI

OpenCode is not a separate `creator.agent` value. Pick the closest harness when running CLI commands:

- OpenAI models → `--agent codex`
- Anthropic models → `--agent claude-code`

Register your model when known, for example:

```bash
uv run articraft external init --agent codex --model-id gpt-5.4 --thinking-level high "$PROMPT"
```

## Hard rules

- Use `uv run articraft external init` for new objects; use `external fork` to edit existing records.
- Edit only the active `model=` path printed by the CLI (usually under `data/records/<id>/revisions/<revision_id>/model.py`).
- Run `uv run articraft external check <record_dir>` until it passes; use `external finalize` only when appropriate.
- Do not manually create `data/records/<id>` folders, copy parent record trees, or write under `traces/`.
- Preserve `creator.mode=external_agent`, `creator.trace_available=false`, and the chosen `creator.agent`.
- Do not promote to the dataset unless the user asked for dataset contribution.

## Quality loop

1. Read the user prompt and identify real-world scale, materials, mechanisms, and controls.
2. Search strong references: `uv run articraft external examples --query "..." --rating-min 5`
3. Build realistic connected geometry with meaningful articulation and semantic link names.
4. Add prompt-specific checks in `run_tests()`.
5. Iterate with `external check` until clean, then `external finalize` (with `--category-slug` only when requested).

## Environment

Prefer `uv run articraft ...` and `just ...` from the repo root. Run `uv sync --group dev` and `uv run articraft init` if the workspace is fresh.
