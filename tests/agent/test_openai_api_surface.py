from __future__ import annotations

import pytest

from agent.providers.openai_api_surface import (
    normalize_openai_api_surface,
    resolve_openai_api_surface,
    validate_openai_chat_transport,
    validate_openai_provider_options,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, "responses"),
        ("", "responses"),
        ("responses", "responses"),
        ("response", "responses"),
        ("chat", "chat_completions"),
        ("chat_completions", "chat_completions"),
        ("completions", "chat_completions"),
        ("chat-completions", "chat_completions"),
    ],
)
def test_normalize_openai_api_surface_aliases(raw: str | None, expected: str) -> None:
    assert normalize_openai_api_surface(raw) == expected


def test_normalize_openai_api_surface_rejects_auto() -> None:
    with pytest.raises(ValueError, match="Unsupported openai_api surface"):
        normalize_openai_api_surface("auto")


def test_resolve_openai_api_surface_priority() -> None:
    env = {
        "ARTICRAFT_OPENAI_API_SURFACE": "responses",
        "OPENAI_API_SURFACE": "chat_completions",
    }
    assert resolve_openai_api_surface(cli_value="chat_completions", env=env) == "chat_completions"
    assert resolve_openai_api_surface(cli_value=None, env=env) == "responses"
    assert resolve_openai_api_surface(cli_value=None, env={}) == "responses"


def test_validate_openai_chat_transport_rejects_websocket() -> None:
    with pytest.raises(ValueError, match="does not support openai_transport=websocket"):
        validate_openai_chat_transport("chat_completions", "websocket")


def test_validate_openai_provider_options_rejects_non_openai_provider() -> None:
    with pytest.raises(ValueError, match="only supported for provider openai"):
        validate_openai_provider_options(
            provider="gemini",
            openai_api="chat_completions",
            openai_transport="http",
            cli_openai_api="chat_completions",
        )


def test_validate_openai_provider_options_ignores_env_surface_for_non_openai() -> None:
    assert (
        validate_openai_provider_options(
            provider="gemini",
            openai_api="chat_completions",
            openai_transport="http",
            cli_openai_api=None,
        )
        == "responses"
    )


def test_openai_compaction_mode_by_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    from agent.providers.openai_api_surface import openai_compaction_mode

    assert openai_compaction_mode("responses") == "api_responses_only"
    monkeypatch.delenv("ARTICRAFT_OPENAI_CHAT_LOCAL_COMPACTION", raising=False)
    assert openai_compaction_mode("chat_completions") == "local_tail"
    monkeypatch.setenv("ARTICRAFT_OPENAI_CHAT_LOCAL_COMPACTION", "0")
    assert openai_compaction_mode("chat_completions") == "none"


def test_chat_local_compaction_truncates_old_tool_output() -> None:
    from agent.providers.chat_local_compaction import (
        compact_chat_messages_in_place,
        partition_chat_messages,
    )

    messages = [
        {"role": "user", "content": "build a latch"},
        {
            "role": "assistant",
            "content": "reading docs",
            "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": "read_file", "arguments": "{}"}}],
        },
        {"role": "tool", "tool_call_id": "call_1", "name": "read_file", "content": "x" * 5000},
        {"role": "assistant", "content": "latest turn"},
    ]
    immutable_end, raw_tail_start = partition_chat_messages(messages)
    assert immutable_end == 1
    assert raw_tail_start == 3
    before, after, count = compact_chat_messages_in_place(
        messages,
        immutable_end=immutable_end,
        raw_tail_start=raw_tail_start,
        max_tool_chars=4000,
        read_file_max_chars=2500,
    )
    assert count == 1
    assert after < before
    assert len(messages[2]["content"]) < 5000
    assert "local compaction truncated" in messages[2]["content"]
