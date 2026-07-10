"""Local tail compaction for Chat Completions conversations."""

from __future__ import annotations

import json
import os

_COMPACTION_MARKER = "\n\n[... local compaction truncated {removed} chars ...]\n\n"


def chat_local_compaction_enabled(env: dict[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    raw = (values.get("ARTICRAFT_OPENAI_CHAT_LOCAL_COMPACTION") or "auto").strip().lower()
    if raw in {"0", "false", "no", "off", "disabled"}:
        return False
    if raw in {"1", "true", "yes", "on", "auto"}:
        return True
    raise ValueError(
        f"Unsupported ARTICRAFT_OPENAI_CHAT_LOCAL_COMPACTION={raw!r}. "
        "Use auto, 1, or 0."
    )


def max_tool_chars_from_env(env: dict[str, str] | None = None) -> int:
    values = os.environ if env is None else env
    raw = (values.get("ARTICRAFT_OPENAI_CHAT_LOCAL_COMPACTION_MAX_TOOL_CHARS") or "4000").strip()
    try:
        parsed = int(raw.replace("_", ""))
    except ValueError as exc:
        raise ValueError(
            "ARTICRAFT_OPENAI_CHAT_LOCAL_COMPACTION_MAX_TOOL_CHARS must be an integer"
        ) from exc
    return max(256, parsed)


def read_file_max_chars_from_env(env: dict[str, str] | None = None) -> int:
    values = os.environ if env is None else env
    raw = (
        values.get("ARTICRAFT_OPENAI_CHAT_LOCAL_COMPACTION_READ_FILE_CHARS") or "2500"
    ).strip()
    try:
        parsed = int(raw.replace("_", ""))
    except ValueError as exc:
        raise ValueError(
            "ARTICRAFT_OPENAI_CHAT_LOCAL_COMPACTION_READ_FILE_CHARS must be an integer"
        ) from exc
    return max(128, parsed)


def partition_chat_messages(messages: list[dict]) -> tuple[int, int]:
    if not messages:
        return 0, 0

    immutable_end = 0
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        if role == "assistant":
            break
        if role == "user":
            immutable_end = index + 1
        else:
            break

    last_assistant: int | None = None
    for index in range(len(messages) - 1, immutable_end - 1, -1):
        message = messages[index]
        if isinstance(message, dict) and message.get("role") == "assistant":
            last_assistant = index
            break

    raw_tail_start = last_assistant if last_assistant is not None else len(messages)
    raw_tail_start = max(immutable_end, min(raw_tail_start, len(messages)))
    return immutable_end, raw_tail_start


def estimate_messages_chars(messages: list[dict]) -> int:
    try:
        return len(json.dumps(messages, ensure_ascii=False, separators=(",", ":")))
    except Exception:
        return sum(len(str(message)) for message in messages)


def _truncate_tool_content(content: str, *, max_chars: int) -> tuple[str, bool]:
    if len(content) <= max_chars:
        return content, False
    if max_chars < 96:
        return content[:max_chars], True

    head_chars = min(400, max(64, max_chars // 4))
    tail_chars = max_chars - head_chars - 64
    if tail_chars < 32:
        head_chars = max_chars // 2
        tail_chars = max_chars - head_chars - 64
    removed = len(content) - (head_chars + tail_chars)
    marker = _COMPACTION_MARKER.format(removed=removed)
    compacted = content[:head_chars] + marker + content[-tail_chars:]
    if len(compacted) > max_chars:
        compacted = compacted[:max_chars]
    return compacted, True


def compact_chat_messages_in_place(
    messages: list[dict],
    *,
    immutable_end: int,
    raw_tail_start: int,
    max_tool_chars: int,
    read_file_max_chars: int,
) -> tuple[int, int, int]:
    before_chars = estimate_messages_chars(messages)
    compacted_count = 0
    for index in range(immutable_end, raw_tail_start):
        message = messages[index]
        if not isinstance(message, dict) or message.get("role") != "tool":
            continue
        content = message.get("content")
        if not isinstance(content, str) or not content:
            continue
        tool_name = message.get("name")
        limit = read_file_max_chars if tool_name == "read_file" else max_tool_chars
        new_content, changed = _truncate_tool_content(content, max_chars=limit)
        if changed:
            message["content"] = new_content
            compacted_count += 1
    after_chars = estimate_messages_chars(messages)
    return before_chars, after_chars, compacted_count
