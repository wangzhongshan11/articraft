from __future__ import annotations

import asyncio
from pathlib import Path

from agent.harness_guidance import GuidanceInjector
from agent.text_io import read_text_path
from agent.tools.write_code import WriteFileTool


def _write_scaffold(script_path: Path, *, editable_code: str) -> None:
    script_path.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "",
                'DEFAULT_NAME = "draft_model"',
                "",
                "# >>> USER_CODE_START",
                editable_code.rstrip(),
                "# >>> USER_CODE_END",
                "",
                "UNCHANGED_SENTINEL = True",
                "",
            ]
        ),
        encoding="utf-8",
    )


async def _run_write(script_path: Path, content: str):
    tool = WriteFileTool()
    invocation = await tool.build({"content": content, "path": "model.py"})
    invocation.bind_file_path(str(script_path))
    return await invocation.execute()


def test_write_file_persists_utf8_when_editable_code_contains_cjk(tmp_path: Path) -> None:
    script_path = tmp_path / "model.py"
    cjk_code = """
def build_object_model():
    return {"source_prompt": "桌面级折叠三脚架手机/小相机支架"}


def run_tests():
    return None
"""
    _write_scaffold(script_path, editable_code='return {"name": "draft_model"}')

    result = asyncio.run(_run_write(script_path, cjk_code))

    assert result.error is None
    data = script_path.read_bytes()
    text = data.decode("utf-8")
    assert "桌面级折叠三脚架" in text
    assert b"\xd7\xc0" not in data


def test_guidance_scan_reads_utf8_model_after_write_file(tmp_path: Path) -> None:
    script_path = tmp_path / "model.py"
    cjk_code = """
def build_object_model():
    return {"source_prompt": "桌面级折叠三脚架手机/小相机支架"}


def run_tests():
    return None
"""
    _write_scaffold(script_path, editable_code='return {"name": "draft_model"}')

    result = asyncio.run(_run_write(script_path, cjk_code))
    assert result.error is None

    injector = GuidanceInjector(
        file_path=str(script_path),
        trace_writer=None,
        tool_call_name=lambda tool_call: tool_call.get("function", {}).get("name", ""),
    )

    assert injector._scan_current_code_contracts() is not None
    assert "桌面级折叠三脚架" in read_text_path(script_path)


def test_guidance_scan_tolerates_legacy_non_utf8_files(tmp_path: Path) -> None:
    script_path = tmp_path / "model.py"
    script_path.write_bytes(b'meta = {"source_prompt": "\xd7\xc0\xc3\xe6"}\n')

    injector = GuidanceInjector(
        file_path=str(script_path),
        trace_writer=None,
        tool_call_name=lambda tool_call: tool_call.get("function", {}).get("name", ""),
    )

    assert injector._scan_current_code_contracts() is None
