"""Console and Unicode safety for agent TUI (Windows GBK consoles, piped stdout)."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from typing import IO, TextIO

from rich.console import Console

_CHECK_MARK = "\u2713"
_CROSS_MARK = "\u2717"
_BOX_RULE = "\u2500"


def ensure_utf8_stdio() -> None:
    """Best-effort UTF-8 stdio for piped subprocesses and legacy Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if not callable(reconfigure):
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            continue


@lru_cache(maxsize=16)
def _encoding_supports_text(encoding: str | None, text: str) -> bool:
    normalized = (encoding or "utf-8").strip() or "utf-8"
    try:
        text.encode(normalized)
        return True
    except (LookupError, UnicodeEncodeError):
        return False


def stream_encoding(stream: IO[str] | TextIO | None) -> str:
    if stream is None:
        stream = sys.stdout
    encoding = getattr(stream, "encoding", None)
    return (encoding or "utf-8").strip() or "utf-8"


def stream_is_interactive(stream: IO[str] | TextIO | None = None) -> bool:
    if stream is None:
        stream = sys.stdout
    isatty = getattr(stream, "isatty", None)
    return bool(isatty and isatty())


def use_unicode_markers(stream: IO[str] | TextIO | None = None) -> bool:
    if stream is None:
        stream = sys.stdout
    encoding = stream_encoding(stream)
    return (
        _encoding_supports_text(encoding, _CHECK_MARK)
        and _encoding_supports_text(encoding, _CROSS_MARK)
        and _encoding_supports_text(encoding, _BOX_RULE)
    )


def success_marker(*, stream: IO[str] | TextIO | None = None) -> str:
    return _CHECK_MARK if use_unicode_markers(stream) else "OK"


def failure_marker(*, stream: IO[str] | TextIO | None = None) -> str:
    return _CROSS_MARK if use_unicode_markers(stream) else "X"


def rule_separator(width: int = 40, *, stream: IO[str] | TextIO | None = None) -> str:
    char = _BOX_RULE if use_unicode_markers(stream) else "-"
    return char * width


def create_agent_console(*, file: TextIO | None = None) -> Console:
    stream = file if file is not None else sys.stdout
    is_tty = stream_is_interactive(stream)
    return Console(
        file=stream,
        force_terminal=is_tty,
        legacy_windows=False,
        no_color=not is_tty,
        width=180 if not is_tty else None,
    )


def utf8_subprocess_env(base: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if base is None else base)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def tui_enabled_from_env(env: dict[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    return values.get("URDF_TUI_ENABLED", "1") != "0"
