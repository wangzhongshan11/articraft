---
description: Fork an existing record for external-agent edits ($1 = record path, rest = edit prompt)
agent: articraft
---

Fork and edit an existing Articraft record.

- Parent record path: **$1**
- Edit request: **$2** (and any further args joined into the prompt)

Follow @EXTERNAL_AGENT_DATA.md and @docs/record_editing.md.

1. Run (pick `codex` or `claude-code` to match your model provider):

```bash
uv run articraft external fork --agent codex "$1" "$2 $3 $4 $5 $6 $7 $8 $9"
```

2. Edit only the printed active `model=` path from the CLI output.
3. Run `uv run articraft external check` on the child record until it passes.
4. Report the new `record_id` and whether finalize is needed.

Do not manually copy `data/records/` folders.
