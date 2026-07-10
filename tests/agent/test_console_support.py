from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

from agent.tui.console_support import (
    _encoding_supports_text,
    create_agent_console,
    failure_marker,
    success_marker,
    use_unicode_markers,
    utf8_subprocess_env,
)


def test_gbk_encoding_rejects_check_mark() -> None:
    assert _encoding_supports_text("gbk", "\u2713") is False
    assert _encoding_supports_text("utf-8", "\u2713") is True


def test_markers_fallback_on_gbk_stream() -> None:
    stream = io.TextIOWrapper(io.BytesIO(), encoding="gbk", errors="strict")
    try:
        assert use_unicode_markers(stream) is False
        assert success_marker(stream=stream) == "OK"
        assert failure_marker(stream=stream) == "X"
    finally:
        stream.detach()


def test_markers_use_unicode_on_utf8_stream() -> None:
    stream = io.StringIO()
    assert use_unicode_markers(stream) is True
    assert success_marker(stream=stream) == "\u2713"
    assert failure_marker(stream=stream) == "\u2717"


def test_create_agent_console_disables_legacy_windows() -> None:
    buffer = io.StringIO()
    console = create_agent_console(file=buffer)
    assert console.legacy_windows is False


def test_utf8_subprocess_env_sets_python_utf8_flags() -> None:
    env = utf8_subprocess_env({"FOO": "bar"})
    assert env["FOO"] == "bar"
    assert env["PYTHONUTF8"] == "1"
    assert env["PYTHONIOENCODING"] == "utf-8"


def test_run_case_child_stdio_is_utf8_under_batch_env() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    env = utf8_subprocess_env()
    env["URDF_TUI_ENABLED"] = "1"
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import os, sys; "
                "print(sys.stdout.encoding); "
                "from agent.tui.single_run import SingleRunDisplay; "
                "from agent.tui.console_support import create_agent_console; "
                "d = SingleRunDisplay("
                "console=create_agent_console(), "
                "model_id='gpt-5.4', thinking_level='med', max_turns=1, enabled=True); "
                "d.start(); "
                "d.add_tool_call('read_file', {}, True, 0.01, result='ok')"
            ),
        ],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert (completed.stdout.splitlines()[0] or "").lower().startswith("utf")
    assert "\u2713" in completed.stdout or " OK " in completed.stdout
