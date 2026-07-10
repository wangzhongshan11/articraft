from __future__ import annotations

import pytest

from agent.providers.openai_edit_mode import (
    openai_use_function_edit_tools,
    validate_openai_chat_edit_tools,
)


def test_openai_function_edit_tools_auto_official_default() -> None:
    assert (
        openai_use_function_edit_tools(
            {
                "OPENAI_BASE_URL": "",
                "ARTICRAFT_OPENAI_FUNCTION_EDIT_TOOLS": "auto",
            }
        )
        is False
    )


def test_openai_function_edit_tools_auto_oneapi() -> None:
    assert (
        openai_use_function_edit_tools(
            {
                "OPENAI_BASE_URL": "https://oneapi-beta.qunhequnhe.com/v1",
                "ARTICRAFT_OPENAI_FUNCTION_EDIT_TOOLS": "auto",
            }
        )
        is True
    )


def test_openai_function_edit_tools_force_custom() -> None:
    assert (
        openai_use_function_edit_tools(
            {
                "OPENAI_BASE_URL": "https://oneapi-beta.qunhequnhe.com/v1",
                "ARTICRAFT_OPENAI_FUNCTION_EDIT_TOOLS": "custom",
            }
        )
        is False
    )


def test_openai_function_edit_tools_force_function() -> None:
    assert (
        openai_use_function_edit_tools(
            {
                "OPENAI_BASE_URL": "",
                "ARTICRAFT_OPENAI_FUNCTION_EDIT_TOOLS": "function",
            }
        )
        is True
    )


def test_validate_openai_chat_edit_tools_requires_function_mode() -> None:
    env = {
        "OPENAI_BASE_URL": "",
        "ARTICRAFT_OPENAI_FUNCTION_EDIT_TOOLS": "custom",
    }
    with pytest.raises(ValueError, match="requires function edit tools"):
        validate_openai_chat_edit_tools("chat_completions", env=env)

    env["ARTICRAFT_OPENAI_FUNCTION_EDIT_TOOLS"] = "function"
    validate_openai_chat_edit_tools("chat_completions", env=env)


def test_validate_openai_chat_edit_tools_ignores_responses() -> None:
    validate_openai_chat_edit_tools(
        "responses",
        env={"ARTICRAFT_OPENAI_FUNCTION_EDIT_TOOLS": "custom"},
    )
