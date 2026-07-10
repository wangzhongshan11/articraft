"""Shared Chat Completions message/tool conversion for OpenAI-compatible APIs."""

from __future__ import annotations

import base64
import json
import mimetypes
import uuid
from pathlib import Path
from typing import Any


def convert_chat_messages(messages: list[dict]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        if role == "user":
            converted.append({"role": "user", "content": convert_message_content(message)})
            continue
        if role == "assistant":
            assistant: dict[str, Any] = {"role": "assistant"}
            content = message.get("content")
            assistant["content"] = content if isinstance(content, str) else None
            tool_calls = message.get("tool_calls")
            if tool_calls:
                assistant["tool_calls"] = tool_calls
            converted.append(assistant)
            continue
        if role == "tool":
            tool_message: dict[str, Any] = {
                "role": "tool",
                "tool_call_id": message.get("tool_call_id") or message.get("call_id"),
                "content": message.get("content") or "",
            }
            name = message.get("name")
            if isinstance(name, str) and name:
                tool_message["name"] = name
            converted.append(tool_message)
    return converted


def convert_message_content(message: dict[str, Any]) -> Any:
    content = message.get("content")
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""

    parts: list[dict[str, Any]] = []
    for part in content:
        if not isinstance(part, dict):
            continue
        part_type = part.get("type")
        if part_type in {"input_text", "text"}:
            text = part.get("text")
            if isinstance(text, str) and text:
                parts.append({"type": "text", "text": text})
            continue
        if part_type == "input_image":
            image = convert_image_part(part)
            if image:
                parts.append(image)
    return parts or ""


def convert_image_part(part: dict[str, Any]) -> dict[str, Any] | None:
    detail = part.get("detail")
    url = part.get("image_url")
    if not isinstance(url, str) or not url:
        image_path = part.get("image_path")
        if isinstance(image_path, str) and image_path:
            url = image_path_to_data_url(image_path)
    if not isinstance(url, str) or not url:
        return None

    image_url: dict[str, Any] = {"url": url}
    if isinstance(detail, str) and detail:
        image_url["detail"] = detail
    return {"type": "image_url", "image_url": image_url}


def convert_tools_for_chat(tools: list[dict]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for tool in tools or []:
        if not isinstance(tool, dict) or tool.get("type") != "function":
            continue
        func = tool.get("function") if isinstance(tool.get("function"), dict) else None
        if not func:
            continue
        converted.append(
            {
                "type": "function",
                "function": {
                    "name": func.get("name", ""),
                    "description": func.get("description", ""),
                    "parameters": func.get("parameters") or {"type": "object"},
                },
            }
        )
    return converted


def serialize_tool_calls(tool_calls: Any) -> list[dict[str, Any]]:
    if not tool_calls:
        return []
    serialized: list[dict[str, Any]] = []
    for tool_call in tool_calls:
        item = serialize_json_value(tool_call)
        if not isinstance(item, dict):
            continue
        call_id = item.get("id") or f"call_{uuid.uuid4().hex}"
        function = item.get("function") if isinstance(item.get("function"), dict) else {}
        serialized.append(
            {
                "id": call_id,
                "type": item.get("type") or "function",
                "function": {
                    "name": str(function.get("name") or ""),
                    "arguments": str(function.get("arguments") or ""),
                },
            }
        )
    return serialized


def extract_chat_usage(response: Any) -> dict[str, int] | None:
    usage = _get(response, "usage")
    if usage is None:
        return None

    def get(field: str) -> Any:
        return _get(usage, field)

    def get_from(obj: Any, field: str) -> Any:
        return _get(obj, field) if obj is not None else None

    prompt_tokens = get("prompt_tokens")
    completion_tokens = get("completion_tokens")
    total_tokens = get("total_tokens")
    cached_tokens = get("cached_tokens")
    reasoning_tokens = None
    details = get("prompt_tokens_details")
    if not isinstance(cached_tokens, int):
        cached_tokens = get_from(details, "cached_tokens")
    completion_details = get("completion_tokens_details")
    reasoning_tokens = get_from(completion_details, "reasoning_tokens")

    cleaned: dict[str, int] = {}
    if isinstance(prompt_tokens, int):
        cleaned["prompt_tokens"] = prompt_tokens
    if isinstance(completion_tokens, int):
        cleaned["candidates_tokens"] = completion_tokens
    if isinstance(total_tokens, int):
        cleaned["total_tokens"] = total_tokens
    if isinstance(cached_tokens, int):
        cleaned["cached_tokens"] = cached_tokens
    if isinstance(reasoning_tokens, int):
        cleaned["reasoning_tokens"] = reasoning_tokens
    return cleaned or None


def serialize_json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [serialize_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [serialize_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize_json_value(child) for key, child in value.items()}
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        return dump(mode="json", exclude_none=True, warnings="none")
    dump_json = getattr(value, "model_dump_json", None)
    if callable(dump_json):
        return json.loads(dump_json(exclude_none=True))
    attrs = getattr(value, "__dict__", None)
    if isinstance(attrs, dict):
        return {
            str(key): serialize_json_value(child)
            for key, child in attrs.items()
            if not key.startswith("_")
        }
    return str(value)


def first_choice(response: Any) -> Any:
    choices = _get(response, "choices")
    if isinstance(choices, list) and choices:
        return choices[0]
    return None


def image_path_to_data_url(image_path: str) -> str:
    path = Path(image_path).expanduser().resolve()
    mime_type, _ = mimetypes.guess_type(path.name)
    if not mime_type:
        mime_type = "application/octet-stream"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{data}"


def _get(obj: Any, field: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(field)
    return getattr(obj, field, None)
