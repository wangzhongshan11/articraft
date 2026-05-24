---
description: Create a new external-agent Articraft record from a prompt
agent: articraft
---

Create a new Articraft record for prompt: **$ARGUMENTS**

Follow @EXTERNAL_AGENT_DATA.md.

1. If the repo is not initialized, run `uv sync --group dev` and `uv run articraft init`.
2. Choose `--agent codex` for OpenAI-backed models or `--agent claude-code` for Anthropic-backed models (OpenCode default: codex unless the user says otherwise).
3. Run:

```bash
uv run articraft external init --agent codex --model-id gpt-5.4 --thinking-level high "$ARGUMENTS"
```

Adjust `--agent`, `--model-id`, and `--thinking-level` to match the user's configured model when known.

4. Edit only the printed active `model=` path. Read SDK docs/examples before writing geometry.
5. Run `uv run articraft external check <record_dir>` and iterate until it passes.
6. Summarize `record_id`, paths, and next steps (finalize vs workbench-only).
