---
description: Bootstrap Articraft Python deps, data tree, and viewer frontend
agent: articraft
---

Bootstrap this Articraft workspace for local development.

1. Ensure `uv` and `just` are on PATH (Homebrew: `brew install uv just`).
2. Run from the repository root:

```bash
export PATH="/opt/homebrew/bin:$PATH"
just setup
```

If `npm ci` fails because a corporate registry is unreachable, retry:

```bash
export NPM_CONFIG_REGISTRY=https://registry.npmjs.org/
npm --prefix viewer/web ci --registry https://registry.npmjs.org/
npm --prefix viewer/web run typecheck
uv run articraft init
```

3. Report `uv run articraft status` output.
4. Tell the user how to start the viewer: `just viewer-dev` (http://127.0.0.1:5173/) or `just viewer` (http://127.0.0.1:8765/).

Do not ask unnecessary questions; fix obvious failures and continue.
