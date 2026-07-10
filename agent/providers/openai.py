"""
OpenAI LLM wrapper using the Responses API with tool calling support.

This module intentionally avoids importing `openai` at import-time so the rest of
the repo can be used without OpenAI installed.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse, urlunparse

from agent.providers.base import (
    ContextWindowPressure,
    PrepareRequestResult,
)
from agent.providers.openai_api_surface import (
    normalize_openai_api_surface,
    validate_openai_chat_transport,
)
from articraft.values import ThinkingLevel, provider_reasoning_level

try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:  # pragma: no cover

    def load_dotenv(*args: Any, **kwargs: Any) -> None:  # type: ignore
        return None


logger = logging.getLogger(__name__)


DEFAULT_OPENAI_MODEL = "gpt-5.5"
_GPT_5_4_AND_5_5_DANGER_ZONE_TOKENS = 272_000
_GPT_5_2_AND_5_3_CODEX_DANGER_ZONE_TOKENS = 280_000
DEFAULT_OPENAI_COMPACTION_MODEL = DEFAULT_OPENAI_MODEL


def _load_cwd_dotenv_override() -> None:
    dotenv_path = Path.cwd() / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=True)


def openai_api_keys_from_env(env: dict[str, str] | None = None) -> list[str]:
    values = os.environ if env is None else env

    def _split(raw: str | None) -> list[str]:
        if not raw:
            return []
        return [token.strip() for token in raw.replace("\n", ",").split(",") if token.strip()]

    keys: list[str] = []
    primary_key = values.get("OPENAI_API_KEY")
    if primary_key and primary_key.strip():
        keys.append(primary_key.strip())
    keys.extend(_split(values.get("OPENAI_API_KEYS")))

    unique_keys: list[str] = []
    seen: set[str] = set()
    for key in keys:
        if key in seen:
            continue
        unique_keys.append(key)
        seen.add(key)
    return unique_keys


def openai_api_key_from_env(env: dict[str, str] | None = None) -> str | None:
    keys = openai_api_keys_from_env(env)
    return random.choice(keys) if keys else None


class OpenAILLM:
    """Minimal OpenAI Responses API client for tool-calling workflows."""

    def __init__(
        self,
        model_id: str = DEFAULT_OPENAI_MODEL,
        *,
        compaction_model_id: Optional[str] = None,
        thinking_level: str = "high",
        reasoning_summary: Optional[str] = "auto",
        transport: str = "http",
        api_surface: str = "responses",
        prompt_cache_key: Optional[str] = None,
        prompt_cache_retention: Optional[str] = None,
        store: Optional[bool] = None,
        dry_run: bool = False,
    ):
        self.model_id = model_id
        self.thinking_level = thinking_level
        self.api_surface = normalize_openai_api_surface(api_surface)
        self.compaction_model_id = (compaction_model_id or DEFAULT_OPENAI_COMPACTION_MODEL).strip()
        self.reasoning_effort = _effort_from_thinking_level(thinking_level)
        self.reasoning_summary = _normalize_reasoning_summary(reasoning_summary)
        self.transport = _normalize_transport(transport)
        validate_openai_chat_transport(self.api_surface, self.transport)
        self.prompt_cache_key = _normalize_prompt_cache_key(prompt_cache_key)
        self.prompt_cache_retention = _normalize_prompt_cache_retention(prompt_cache_retention)
        self.store = self.transport == "websocket" if store is None else bool(store)
        # Hard timeout for a single OpenAI request. Set to 0/negative to disable.
        self.request_timeout_seconds = _env_float("OPENAI_REQUEST_TIMEOUT_SECONDS", 900.0)
        self.max_attempts = max(1, int(_env_float("OPENAI_MAX_ATTEMPTS", 4)))
        self.retry_base_seconds = _env_float("OPENAI_RETRY_BASE_SECONDS", 0.5)
        self.retry_max_seconds = _env_float("OPENAI_RETRY_MAX_SECONDS", 20.0)
        self.websocket_open_timeout_seconds = _env_float(
            "OPENAI_WEBSOCKET_OPEN_TIMEOUT_SECONDS", 20.0
        )
        # Rotate the socket before the documented 60 minute server cap.
        self.websocket_max_connection_age_seconds = _env_float(
            "OPENAI_WEBSOCKET_MAX_CONNECTION_AGE_SECONDS", 3300.0
        )
        self._api_key: Optional[str] = None
        if dry_run:
            self._client = None
            self._client_is_async = False
        else:
            _load_cwd_dotenv_override()
            api_key = openai_api_key_from_env()
            if not api_key:
                raise ValueError(
                    "OpenAI credentials not found. Set OPENAI_API_KEY or OPENAI_API_KEYS."
                )
            self._api_key = api_key

            self._client: Any
            self._client_is_async: bool
            client_kwargs: dict[str, Any] = {
                "api_key": api_key,
                # Disable SDK-managed retries so request timing and retry policy are
                # controlled by this wrapper rather than hidden nested backoff.
                "max_retries": 0,
            }
            base_url = os.environ.get("OPENAI_BASE_URL", "").strip()
            if base_url:
                client_kwargs["base_url"] = base_url.rstrip("/")
            if self.request_timeout_seconds and self.request_timeout_seconds > 0:
                client_kwargs["timeout"] = float(self.request_timeout_seconds)
            try:
                from openai import AsyncOpenAI  # type: ignore

                self._client = AsyncOpenAI(**client_kwargs)
                self._client_is_async = True
            except Exception:
                try:
                    from openai import OpenAI  # type: ignore
                except Exception as exc:  # pragma: no cover
                    raise RuntimeError(
                        "OpenAI provider selected but the `openai` package is not installed. "
                        "Install it (e.g. `uv add openai`), then try again."
                    ) from exc

                self._client = OpenAI(**client_kwargs)
                self._client_is_async = False

        resolved_base_url = os.environ.get("OPENAI_BASE_URL", "").strip().rstrip("/") or None
        if resolved_base_url is None:
            client_base_url = getattr(getattr(self, "_client", None), "base_url", None)
            if client_base_url is not None:
                resolved_base_url = str(client_base_url).rstrip("/")
        self._responses_websocket_url = _responses_websocket_url(resolved_base_url)

        self._chat_backend: Any = None
        self._responses_backend: Any = None
        if self.api_surface == "chat_completions":
            from agent.providers.openai_chat_backend import OpenAIChatBackend

            self._chat_backend = OpenAIChatBackend(self)
        else:
            from agent.providers.openai_responses_backend import OpenAIResponsesBackend

            self._responses_backend = OpenAIResponsesBackend(self)

    _RESPONSES_BACKEND_STATE = frozenset(
        {
            "_input_items",
            "_pending_incremental_input_items",
            "_last_message_count",
            "_previous_response_id",
            "_last_response_start_index",
            "_last_usage",
            "_last_compaction_turn_number",
            "_last_soft_compaction_failure_sig",
            "_last_soft_compaction_turn_number",
            "_last_soft_compaction_prompt_tokens",
            "_unsupported_threshold_event_emitted",
            "_websocket",
            "_websocket_opened_at",
        }
    )

    def __getattr__(self, name: str) -> Any:
        backend = object.__getattribute__(self, "_responses_backend")
        if backend is not None and name in self._RESPONSES_BACKEND_STATE:
            return getattr(backend, name)
        if backend is not None and name.startswith("_") and hasattr(backend, name):
            return getattr(backend, name)
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._RESPONSES_BACKEND_STATE:
            try:
                backend = object.__getattribute__(self, "_responses_backend")
            except AttributeError:
                backend = None
            if backend is not None:
                setattr(backend, name, value)
                return
        try:
            backend = object.__getattribute__(self, "_responses_backend")
        except AttributeError:
            backend = None
        if backend is not None and hasattr(backend, name):
            setattr(backend, name, value)
            return
        object.__setattr__(self, name, value)

    def build_request_preview(
        self,
        *,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
    ) -> dict[str, Any]:
        if self._chat_backend is not None:
            return self._chat_backend.build_request_preview(
                system_prompt=system_prompt,
                messages=messages,
                tools=tools,
            )
        return self._responses_backend.build_request_preview(
            system_prompt=system_prompt,
            messages=messages,
            tools=tools,
        )

    def context_window_pressure(self, usage: dict[str, int]) -> ContextWindowPressure:
        if self._chat_backend is not None:
            return self._chat_backend.context_window_pressure(usage)
        return self._responses_backend.context_window_pressure(usage)

    async def prepare_next_request(
        self,
        *,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
        completed_turns: int,
        consecutive_compile_failure_count: int = 0,
        last_compile_failure_sig: Optional[str] = None,
    ) -> PrepareRequestResult:
        if self._chat_backend is not None:
            return await self._chat_backend.prepare_next_request(
                system_prompt=system_prompt,
                messages=messages,
                tools=tools,
                completed_turns=completed_turns,
                consecutive_compile_failure_count=consecutive_compile_failure_count,
                last_compile_failure_sig=last_compile_failure_sig,
            )
        return await self._responses_backend.prepare_next_request(
            system_prompt=system_prompt,
            messages=messages,
            tools=tools,
            completed_turns=completed_turns,
            consecutive_compile_failure_count=consecutive_compile_failure_count,
            last_compile_failure_sig=last_compile_failure_sig,
        )

    async def generate_with_tools(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
    ) -> dict:
        if self._chat_backend is not None:
            return await self._chat_backend.generate_with_tools(
                system_prompt,
                messages,
                tools,
            )
        return await self._responses_backend.generate_with_tools(
            system_prompt,
            messages,
            tools,
        )

    async def close(self) -> None:
        if self._chat_backend is not None:
            await self._chat_backend.close()
        elif self._responses_backend is not None:
            await self._responses_backend.close()
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


def _hard_pressure_threshold_for_model(model_id: str) -> int | None:
    normalized = (model_id or "").strip().lower()
    if normalized.startswith("gpt-5.4") or normalized.startswith("gpt-5.5"):
        return _GPT_5_4_AND_5_5_DANGER_ZONE_TOKENS
    if normalized.startswith("gpt-5.2") or normalized.startswith("gpt-5.3-codex"):
        return _GPT_5_2_AND_5_3_CODEX_DANGER_ZONE_TOKENS
    return None


def _context_window_tokens_for_model(model_id: str) -> int | None:
    override = _env_int_or_none("OPENAI_CONTEXT_WINDOW_TOKENS")
    if override is not None:
        return override

    normalized = (model_id or "").strip().lower()
    if normalized.startswith(("gpt-5.2", "gpt-5.3-codex", "gpt-5.4", "gpt-5.5")):
        return 400_000
    if normalized.startswith("gpt-4.1"):
        return 1_000_000
    return None


def _normalize_reasoning_summary(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.lower() in {"0", "false", "none", "off"}:
        return None
    return text


def _normalize_prompt_cache_key(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text


def _normalize_prompt_cache_retention(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.lower() in {"0", "false", "none", "off"}:
        return None
    return text


def _effort_from_thinking_level(thinking_level: str) -> str:
    return provider_reasoning_level(thinking_level, default=ThinkingLevel.MED)


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw.strip())
    except Exception:
        return default


def _env_int_or_none(name: str) -> int | None:
    raw = os.environ.get(name)
    if raw is None:
        return None
    try:
        value = int(raw.strip().replace("_", ""))
    except Exception:
        return None
    return value if value > 0 else None


def _normalize_transport(transport: str) -> str:
    value = (transport or "http").strip().lower()
    if value not in {"http", "websocket"}:
        raise ValueError(f"Unsupported OpenAI transport: {transport}")
    return value


def _responses_websocket_url(base_url: Optional[str]) -> str:
    root = (base_url or "https://api.openai.com/v1/").strip()
    parsed = urlparse(root)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    path = parsed.path.rstrip("/")
    if not path:
        path = "/v1"
    if not path.endswith("/responses"):
        if not path.endswith("/v1"):
            path = f"{path}/v1"
        path = f"{path}/responses"
    return urlunparse((scheme, parsed.netloc, path, "", "", ""))


def _payload_without_reasoning_summary(request_payload: dict[str, Any]) -> dict[str, Any]:
    updated = dict(request_payload)
    reasoning = updated.get("reasoning")
    if not isinstance(reasoning, dict) or "summary" not in reasoning:
        return updated
    new_reasoning = dict(reasoning)
    new_reasoning.pop("summary", None)
    updated["reasoning"] = new_reasoning
    return updated


def _extract_http_status(exc: BaseException) -> Optional[int]:
    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
    if isinstance(status, int) and 100 <= status <= 599:
        return status
    response = getattr(exc, "response", None)
    if response is not None:
        status = getattr(response, "status_code", None) or getattr(response, "status", None)
        if isinstance(status, int) and 100 <= status <= 599:
            return status
    return None


def _is_chat_reasoning_extra_body_unsupported_error(exc: BaseException) -> bool:
    status = _extract_http_status(exc)
    if status is not None and status not in {400, 422}:
        return False

    message = str(exc).strip().lower()
    if not message:
        return False
    if "reasoning" not in message:
        return False

    return any(
        needle in message
        for needle in (
            "unsupported",
            "not supported",
            "invalid",
            "unknown parameter",
            "not allowed",
            "unrecognized",
            "extra_body",
        )
    )


def _is_reasoning_summary_unsupported_error(exc: BaseException) -> bool:
    status = _extract_http_status(exc)
    if status is not None and status not in {400, 422}:
        return False

    message = str(exc).strip().lower()
    if not message:
        return False

    if "reasoning.summary" in message:
        return any(
            needle in message
            for needle in (
                "unsupported",
                "not supported",
                "invalid",
                "unknown parameter",
                "not allowed",
                "unrecognized",
            )
        )

    if "reasoning" not in message or "summary" not in message:
        return False

    return any(
        needle in message
        for needle in (
            "unsupported",
            "not supported",
            "invalid",
            "unknown parameter",
            "not allowed",
            "unrecognized",
        )
    )


def _should_retry_openai_exception(exc: BaseException) -> bool:
    if isinstance(exc, (asyncio.TimeoutError, TimeoutError)):
        return True

    status = _extract_http_status(exc)
    if status is not None:
        if status in {408, 409, 425, 429, 500, 502, 503, 504}:
            return True
        if 400 <= status < 500:
            return False
        if status >= 500:
            return True

    if isinstance(exc, OpenAIWebSocketError):
        if exc.code == "previous_response_not_found":
            return False
        if exc.code in {
            "websocket_connection_limit_reached",
            "rate_limit_exceeded",
            "server_error",
            "overloaded",
            "temporarily_unavailable",
        }:
            return True

    message = str(exc).lower()
    if any(
        needle in message
        for needle in (
            "overloaded",
            "temporarily unavailable",
            "service unavailable",
            "timeout",
            "timed out",
            "deadline exceeded",
            "rate limit",
            "too many requests",
            "connection reset",
            "connection aborted",
            "connection refused",
            "connection error",
            "internal error",
            "backend error",
        )
    ):
        return True

    if any(
        needle in message
        for needle in (
            "api key",
            "unauthorized",
            "permission denied",
            "forbidden",
            "invalid",
            "malformed",
            "not found",
        )
    ):
        return False

    return True


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
    fn: Any,
    *,
    max_attempts: int,
    should_retry: Any,
    base_delay: float,
    max_delay: float,
    sleep_fn: Any = asyncio.sleep,
    rng: Any = random.random,
    logger: Optional[logging.Logger] = None,
    context: str = "openai",
) -> Any:
    if max_attempts <= 0:
        raise ValueError("max_attempts must be >= 1")

    attempt = 0
    while True:
        try:
            return await fn()
        except Exception as exc:
            attempt += 1
            if attempt >= max_attempts or not bool(should_retry(exc)):
                raise

            cap = min(max_delay, base_delay * (2 ** (attempt - 1)))
            delay = max(0.0, float(rng()) * cap)
            if logger:
                logger.warning(
                    "%s failed (attempt %s/%s), retrying in %.2fs: %s",
                    context,
                    attempt,
                    max_attempts,
                    delay,
                    _format_retry_exception(exc),
                )
            await sleep_fn(delay)


def _response_error_message(response_payload: Any) -> str:
    if response_payload is None:
        return ""
    error = (
        response_payload.get("error")
        if isinstance(response_payload, dict)
        else getattr(response_payload, "error", None)
    )
    if error is None:
        return ""
    if isinstance(error, str):
        return error.strip()
    if isinstance(error, dict):
        message = error.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
        return json.dumps(error)
    message = getattr(error, "message", None)
    if isinstance(message, str) and message.strip():
        return message.strip()
    code = getattr(error, "code", None)
    if isinstance(code, str) and code.strip():
        return code.strip()
    return str(error)


class OpenAIWebSocketError(RuntimeError):
    def __init__(
        self,
        *,
        code: Optional[str],
        message: str,
        status: Optional[int] = None,
        response: Any = None,
    ):
        self.code = code
        self.status = status
        self.response = response
        super().__init__(message)

    @classmethod
    def from_event(cls, event: dict[str, Any]) -> "OpenAIWebSocketError":
        error = event.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if not isinstance(message, str) or not message.strip():
                message = json.dumps(error)
            code = error.get("code")
        else:
            message = str(error or "OpenAI websocket error")
            code = None
        status = event.get("status")
        return cls(
            code=str(code) if code is not None else None,
            message=message,
            status=int(status) if isinstance(status, int) else None,
        )
