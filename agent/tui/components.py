"""Shared constants and tiny helpers for TUI output."""

from typing import IO, TextIO

from rich.text import Text

from agent.tui.console_support import failure_marker, success_marker


def status_icon(success: bool, *, stream: IO[str] | TextIO | None = None) -> Text:
    if success:
        return Text(success_marker(stream=stream), style="green")
    return Text(failure_marker(stream=stream), style="red")
