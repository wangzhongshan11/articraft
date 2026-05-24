---
description: Start the Articraft viewer (dev mode with hot reload)
agent: articraft
---

Start the local Articraft viewer for browsing records.

1. Ensure dependencies exist (`just setup` or prior install). For frontend npm issues use `NPM_CONFIG_REGISTRY=https://registry.npmjs.org/`.
2. From repo root:

```bash
export PATH="/opt/homebrew/bin:$PATH"
just viewer-dev
```

3. Tell the user:
   - Frontend: http://127.0.0.1:5173/
   - API: http://127.0.0.1:8765/health
4. Note that 3D assets materialize on first open if `data/cache/record_materialization/` is empty; optional bulk prep: `uv run articraft compile-all`.

If a viewer is already running on those ports, say so instead of starting a duplicate.
