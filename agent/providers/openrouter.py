"""
OpenRouter LLM wrapper using the OpenAI-compatible Chat Completions API.

This module intentionally avoids importing `openai` at import-time so the rest
of the repo can be used without OpenRouter/OpenAI SDK credentials installed.
"""

from __future__ import annotations

import asyncio
import copy
import json
import logging
import os
import random
from pathlib import Path
from typing import Any

from agent.providers import openai_chat_codec as chat_codec
from agent.providers.base import (
    ContextWindowPressure,
    PrepareRequestResult,
    build_context_window_pressure,
)
from articraft.values import reasoning_level_alias

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover

    def load_dotenv(*args: Any, **kwargs: Any) -> None:  # type: ignore
        return None


logger = logging.getLogger(__name__)

DEFAULT_OPENROUTER_MODEL = "tencent/hy3-preview:free"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_CONTEXT_TOKENS = 262_144
DEFAULT_OPENROUTER_MAX_TOKENS = 262_144
DEFAULT_OPENROUTER_OUTPUT_SAFETY_TOKENS = 1_024


def _load_cwd_dotenv_override() -> None:
    dotenv_path = Path.cwd() / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=True)


def openrouter_api_keys_from_env(env: dict[str, str] | None = None) -> list[str]:
    values = os.environ if env is None else env

    def _split(raw: str | None) -> list[str]:
        if not raw:
            return []
        return [token.strip() for token in raw.replace("\n", ",").split(",") if token.strip()]

    keys: list[str] = []
    primary_key = values.get("OPENROUTER_API_KEY")
    if primary_key and primary_key.strip():
        keys.append(primary_key.strip())
    keys.extend(_split(values.get("OPENROUTER_API_KEYS")))

    unique_keys: list[str] = []
    seen: set[str] = set()
    for key in keys:
        if key in seen:
            continue
        unique_keys.append(key)
        seen.add(key)
    return unique_keys


def openrouter_api_key_from_env(env: dict[str, str] | None = None) -> str | None:
    keys = openrouter_api_keys_from_env(env)
    return random.choice(keys) if keys else None


class OpenRouterLLM:
    """OpenRouter Chat Completions client for tool-calling workflows."""

    def __init__(
        self,
        model_id: str = DEFAULT_OPENROUTER_MODEL,
        *,
        thinking_level: str = "high",
        dry_run: bool = False,
    ):
        self.model_id = model_id
        self.thinking_level = thinking_level
        self.reasoning = _reasoning_config_from_thinking_level(thinking_level)
        self.max_tokens = _env_int(
            "OPENROUTER_MAX_TOKENS",
            _env_int("OPENROUTER_MAX_COMPLETION_TOKENS", DEFAULT_OPENROUTER_MAX_TOKENS),
        )
        self.context_tokens = _env_int(
            "OPENROUTER_CONTEXT_TOKENS",
            DEFAULT_OPENROUTER_CONTEXT_TOKENS,
        )
        self.output_safety_tokens = _env_int(
            "OPENROUTER_OUTPUT_SAFETY_TOKENS",
            DEFAULT_OPENROUTER_OUTPUT_SAFETY_TOKENS,
        )
        self.request_timeout_seconds = _env_float("OPENROUTER_REQUEST_TIMEOUT_SECONDS", 900.0)
        self.max_attempts = max(1, int(_env_float("OPENROUTER_MAX_ATTEMPTS", 4)))
        self.retry_base_seconds = _env_float("OPENROUTER_RETRY_BASE_SECONDS", 0.5)
        self.retry_max_seconds = _env_float("OPENROUTER_RETRY_MAX_SECONDS", 20.0)
        if dry_run:
            self._client = None
            self._client_is_async = False
        else:
            _load_cwd_dotenv_override()
            api_key = openrouter_api_key_from_env()
            if not api_key:
                raise ValueError(
                    "OpenRouter credentials not found. "
                    "Set OPENROUTER_API_KEY or OPENROUTER_API_KEYS."
                )

            client_kwargs: dict[str, Any] = {
                "api_key": api_key,
                "base_url": OPENROUTER_BASE_URL,
                "max_retries": 0,
            }
            default_headers = _openrouter_default_headers()
            if default_headers:
                client_kwargs["default_headers"] = default_headers
            if self.request_timeout_seconds and self.request_timeout_seconds > 0:
                client_kwargs["timeout"] = float(self.request_timeout_seconds)

            self._client: Any
            self._client_is_async: bool
            try:
                from openai import AsyncOpenAI  # type: ignore

                self._client = AsyncOpenAI(**client_kwargs)
                self._client_is_async = True
            except Exception:
                try:
                    from openai import OpenAI  # type: ignore
                except Exception as exc:  # pragma: no cover
                    raise RuntimeError(
                        "OpenRouter provider selected but the `openai` package is not installed. "
                        "Install it (e.g. `uv add openai`), then try again."
                    ) from exc

                self._client = OpenAI(**client_kwargs)
                self._client_is_async = False

    def build_request_preview(
        self,
        *,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
    ) -> dict[str, Any]:
        payload = self._build_chat_payload(
            system_prompt=system_prompt,
            messages=messages,
            tools=tools,
        )
        payload["base_url"] = OPENROUTER_BASE_URL
        return payload

    def context_window_pressure(self, usage: dict[str, int]) -> ContextWindowPressure:
        return build_context_window_pressure(
            provider="openrouter",
            usage=usage,
            max_context_tokens=self.context_tokens,
        )

    async def prepare_next_request(
        self,
        *,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
        completed_turns: int,
        consecutive_compile_failure_count: int = 0,
        last_compile_failure_sig: str | None = None,
    ) -> PrepareRequestResult:
        return PrepareRequestResult()

    async def generate_with_tools(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
    ) -> dict[str, Any]:
        if self._client is None:
            raise RuntimeError("OpenRouter transport is unavailable in dry_run mode")

        request_payload = self._build_chat_payload(
            system_prompt=system_prompt,
            messages=messages,
            tools=tools,
        )

        async def _request_once() -> Any:
            request_coro = self._chat_completion(request_payload)
            if self.request_timeout_seconds and self.request_timeout_seconds > 0:
                return await asyncio.wait_for(
                    request_coro,
                    timeout=float(self.request_timeout_seconds),
                )
            return await request_coro

        response = await _async_retry(
            _request_once,
            max_attempts=self.max_attempts,
            should_retry=_should_retry_openrouter_exception,
            base_delay=self.retry_base_seconds,
            max_delay=self.retry_max_seconds,
            logger=logger,
            context="openrouter[chat.completions]",
        )
        return self._convert_response(response)

    async def close(self) -> None:
        client = getattr(self, "_client", None)
        if client is None:
            return None
        close_method = getattr(client, "close", None)
        if close_method is None:
            return None
        result = close_method()
        if asyncio.iscoroutine(result):
            await result
        return None

    async def _chat_completion(self, request_payload: dict[str, Any]) -> Any:
        payload = dict(request_payload)
        extra_body = payload.pop("extra_body", None)
        if self._client_is_async:
            if extra_body is None:
                return await self._client.chat.completions.create(**payload)
            return await self._client.chat.completions.create(
                **payload,
                extra_body=extra_body,
            )
        if extra_body is None:
            return await asyncio.to_thread(self._client.chat.completions.create, **payload)
        return await asyncio.to_thread(
            self._client.chat.completions.create,
            **payload,
            extra_body=extra_body,
        )

    def _build_chat_payload(
        self,
        *,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
    ) -> dict[str, Any]:
        chat_messages: list[dict[str, Any]] = []
        if system_prompt.strip():
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(_convert_chat_messages(messages))

        payload: dict[str, Any] = {
            "model": self.model_id,
            "messages": chat_messages,
            "extra_body": {"reasoning": copy.deepcopy(self.reasoning)},
        }
        converted_tools = chat_codec.convert_tools_for_chat(tools)
        if converted_tools:
            payload["tools"] = converted_tools
        max_tokens = self._request_max_tokens(payload)
        if max_tokens > 0:
            payload["max_tokens"] = max_tokens
        return payload

    def _request_max_tokens(self, payload: dict[str, Any]) -> int:
        if self.max_tokens <= 0:
            return 0
        if self.context_tokens <= 0:
            return self.max_tokens
        estimated_prompt_tokens = _estimate_prompt_tokens(payload)
        available = (
            self.context_tokens - estimated_prompt_tokens - max(0, self.output_safety_tokens)
        )
        if available <= 0:
            return min(self.max_tokens, 16)
        return min(self.max_tokens, available)

    def _convert_response(self, response: Any) -> dict[str, Any]:
        choice = chat_codec.first_choice(response)
        message = _get(choice, "message")
        if message is None:
            return {}

        content = _get(message, "content")
        tool_calls = chat_codec.serialize_tool_calls(_get(message, "tool_calls"))
        reasoning = _get(message, "reasoning")
        reasoning_details = chat_codec.serialize_json_value(_get(message, "reasoning_details"))
        usage = chat_codec.extract_chat_usage(response)

        result: dict[str, Any] = {
            "content": content if isinstance(content, str) else "",
            "tool_calls": tool_calls,
        }
        thought_summary = _reasoning_details_summary(reasoning_details)
        if not thought_summary and isinstance(reasoning, str):
            thought_summary = reasoning.strip()
        if thought_summary:
            result["thought_summary"] = thought_summary
        if reasoning_details or reasoning:
            result["extra_content"] = {
                "openrouter": {
                    "reasoning": reasoning,
                    "reasoning_details": reasoning_details,
                }
            }
        if usage:
            result["usage"] = usage
        return result


def _convert_chat_messages(messages: list[dict]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        if role == "assistant":
            assistant_messages = chat_codec.convert_chat_messages([message])
            if not assistant_messages:
                continue
            assistant = assistant_messages[0]
            extra_content = message.get("extra_content")
            if isinstance(extra_content, dict):
                openrouter = extra_content.get("openrouter")
                if isinstance(openrouter, dict):
                    reasoning = openrouter.get("reasoning")
                    reasoning_details = openrouter.get("reasoning_details")
                    if reasoning:
                        assistant["reasoning"] = reasoning
                    if reasoning_details:
                        assistant["reasoning_details"] = reasoning_details
            converted.append(assistant)
            continue
        converted.extend(chat_codec.convert_chat_messages([message]))
    return converted


def _get(obj: Any, field: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(field)
    return getattr(obj, field, None)


def _reasoning_config_from_thinking_level(thinking_level: str) -> dict[str, Any]:
    level = reasoning_level_alias(thinking_level)
    if level in {"0", "false", "none", "off", "disabled"}:
        return {"enabled": False}
    reasoning: dict[str, Any] = {"enabled": True}
    if level in {"low", "high"}:
        reasoning["effort"] = level
    return reasoning


def _reasoning_details_summary(reasoning_details: Any) -> str:
    if not isinstance(reasoning_details, list):
        return ""
    fragments: list[str] = []
    for item in reasoning_details:
        if not isinstance(item, dict):
            continue
        text = item.get("summary") or item.get("text")
        if isinstance(text, str) and text.strip():
            fragments.append(text.strip())
    return "\n".join(fragments).strip()


def _estimate_prompt_tokens(payload: dict[str, Any]) -> int:
    """Conservative rough count so max_tokens stays below OpenRouter's context cap."""

    messages = payload.get("messages")
    tools = payload.get("tools")
    text_size = _json_text_size(messages) + _json_text_size(tools)
    # Hy3 uses a tokenizer OpenRouter labels as "Other"; a 3 chars/token estimate
    # intentionally overcounts common English/code text.
    structural_overhead = 128
    if isinstance(messages, list):
        structural_overhead += len(messages) * 16
    if isinstance(tools, list):
        structural_overhead += len(tools) * 128
    return max(1, (text_size + 2) // 3 + structural_overhead)


def _json_text_size(value: Any) -> int:
    if value is None:
        return 0
    try:
        return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")))
    except Exception:
        return len(str(value))


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw.strip())
    except Exception:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw.strip().replace("_", ""))
    except Exception:
        return default


def _openrouter_default_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    referer = os.environ.get("OPENROUTER_HTTP_REFERER") or os.environ.get("OPENROUTER_SITE_URL")
    title = os.environ.get("OPENROUTER_APP_TITLE") or os.environ.get("OPENROUTER_SITE_NAME")
    if referer and referer.strip():
        headers["HTTP-Referer"] = referer.strip()
    if title and title.strip():
        headers["X-OpenRouter-Title"] = title.strip()
    return headers


def _extract_http_status(exc: BaseException) -> int | None:
    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
    if isinstance(status, int) and 100 <= status <= 599:
        return status
    response = getattr(exc, "response", None)
    if response is not None:
        status = getattr(response, "status_code", None) or getattr(response, "status", None)
        if isinstance(status, int) and 100 <= status <= 599:
            return status
    return None


def _should_retry_openrouter_exception(exc: BaseException) -> bool:
    if isinstance(exc, (asyncio.TimeoutError, TimeoutError)):
        return True
    if isinstance(exc, json.JSONDecodeError):
        return True
    status = _extract_http_status(exc)
    if status is not None:
        if status in {408, 409, 425, 429, 500, 502, 503, 504}:
            return True
        if 400 <= status < 500:
            return False
        if status >= 500:
            return True
    message = str(exc).lower()
    return any(
        needle in message
        for needle in (
            "timeout",
            "timed out",
            "connection error",
            "connection reset",
            "connection aborted",
            "server disconnected",
            "protocol error",
            "temporarily unavailable",
            "rate limit",
            "bad gateway",
            "service unavailable",
        )
    )


def _format_retry_exception(exc: BaseException) -> str:
    status = _extract_http_status(exc)
    message = str(exc).strip()
    summary = type(exc).__name__
    if status is not None:
        summary += f" (HTTP {status})"
    if message:
        return f"{summary}: {message}"
    return f"{summary}: {repr(exc)}"


async def _async_retry(
    operation: Any,
    *,
    max_attempts: int,
    should_retry: Any,
    base_delay: float,
    max_delay: float,
    logger: logging.Logger,
    context: str,
    sleep_fn: Any = asyncio.sleep,
    rng: Any = random.random,
) -> Any:
    if max_attempts <= 0:
        raise ValueError("max_attempts must be >= 1")

    attempt = 0
    while True:
        try:
            return await operation()
        except Exception as exc:
            attempt += 1
            if attempt >= max_attempts or not should_retry(exc):
                raise

            cap = min(max_delay, base_delay * (2 ** (attempt - 1)))
            delay = max(0.0, float(rng()) * cap)
            logger.warning(
                "%s failed (attempt %s/%s), retrying in %.2fs: %s",
                context,
                attempt,
                max_attempts,
                delay,
                _format_retry_exception(exc),
            )
            await sleep_fn(delay)
