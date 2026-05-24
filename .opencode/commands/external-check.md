---
description: Run strict external compile/validation on a record ($1 = record dir or id)
agent: articraft
---

Validate record: **$1**

Follow @EXTERNAL_AGENT_DATA.md.

1. Resolve the record directory (accept `data/records/<id>` or a bare record id).
2. Run:

```bash
uv run articraft external check "$1"
```

3. If it fails, read the compile report, fix the active `model.py`, and re-run until it passes.
4. Summarize errors fixed and whether `external finalize` is appropriate.
