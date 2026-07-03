"""
OpenAI edit-tool mode selection.

Official OpenAI Responses API supports Codex-style ``apply_patch`` custom tools.
Many OpenAI-compatible proxies (OneAPI, etc.) only reliably support standard
``type: function`` tool calls — the same shape CAD runtime and Gemini use.
"""

from __future__ import annotations

import os


def openai_use_function_edit_tools(env: dict[str, str] | None = None) -> bool:
    """
    Return True when OpenAI runs should use ``replace`` / ``write_file`` instead
    of the Codex ``apply_patch`` custom tool.

    Controlled by ``ARTICRAFT_OPENAI_FUNCTION_EDIT_TOOLS``:
    - unset / ``auto`` (default): function mode when ``OPENAI_BASE_URL`` is set
      and does not point at ``api.openai.com``
    - ``1`` / ``true`` / ``function``: always function mode
    - ``0`` / ``false`` / ``custom``: always custom ``apply_patch`` mode
    """
    values = os.environ if env is None else env
    override = (values.get("ARTICRAFT_OPENAI_FUNCTION_EDIT_TOOLS") or "auto").strip().lower()
    if override in {"1", "true", "yes", "function", "on"}:
        return True
    if override in {"0", "false", "no", "custom", "off"}:
        return False

    base_url = (values.get("OPENAI_BASE_URL") or "").strip().lower().rstrip("/")
    if not base_url:
        return False
    return "api.openai.com" not in base_url
