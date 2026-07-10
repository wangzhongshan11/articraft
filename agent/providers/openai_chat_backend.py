"""OpenAI Chat Completions backend for tool-calling workflows."""

from __future__ import annotations

import asyncio
import copy
import logging
import os
from typing import TYPE_CHECKING, Any, Optional

from agent.providers import openai_chat_codec as chat_codec
from agent.providers.base import (
    CompactionEvent,
    ContextWindowPressure,
    PrepareRequestResult,
    ProviderTraceEvent,
    build_context_window_pressure,
)
from agent.providers.chat_local_compaction import (
    chat_local_compaction_enabled,
    compact_chat_messages_in_place,
    max_tool_chars_from_env,
    partition_chat_messages,
    read_file_max_chars_from_env,
)
from agent.providers.compaction_policy import decide_compaction
from agent.providers.openai import (
    _async_retry,
    _context_window_tokens_for_model,
    _hard_pressure_threshold_for_model,
    _is_chat_reasoning_extra_body_unsupported_error,
    _should_retry_openai_exception,
)
from articraft.values import ThinkingLevel, provider_reasoning_level

if TYPE_CHECKING:
    from agent.providers.openai import OpenAILLM

logger = logging.getLogger(__name__)


def _chat_reasoning_mode() -> str:
    mode = (os.environ.get("ARTICRAFT_OPENAI_CHAT_REASONING") or "none").strip().lower()
    if mode in {"", "none", "off", "0", "false"}:
        return "none"
    if mode == "extra_body":
        return "extra_body"
    if mode == "auto":
        return "auto"
    raise ValueError(
        f"Unsupported ARTICRAFT_OPENAI_CHAT_REASONING={mode!r}. "
        "Use none, extra_body, or auto."
    )


def _reasoning_extra_body(
    thinking_level: str,
    *,
    reasoning_extra_body_supported: bool | None,
) -> dict[str, Any] | None:
    mode = _chat_reasoning_mode()
    if mode == "none":
        return None
    if mode == "auto" and reasoning_extra_body_supported is False:
        return None
    if mode not in {"extra_body", "auto"}:
        return None
    effort = provider_reasoning_level(thinking_level, default=ThinkingLevel.MED)
    return {"reasoning": {"effort": effort}}


def _field(obj: Any, name: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


class OpenAIChatBackend:
    def __init__(self, host: OpenAILLM) -> None:
        self._host = host
        self._compaction_unavailable_traced = False
        self._unsupported_threshold_event_emitted = False
        self._last_usage: dict[str, int] | None = None
        self._last_compaction_turn_number: int | None = None
        self._last_soft_compaction_failure_sig: str | None = None
        self._last_soft_compaction_turn_number: int | None = None
        self._last_soft_compaction_prompt_tokens: int | None = None
        self._reasoning_extra_body_supported: bool | None = None
        self._reasoning_probe_traced = False

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
        payload["openai_api"] = "chat_completions"
        payload["openai_transport"] = self._host.transport
        return payload

    def context_window_pressure(self, usage: dict[str, int]) -> ContextWindowPressure:
        return build_context_window_pressure(
            provider="openai",
            usage=usage,
            max_context_tokens=_context_window_tokens_for_model(self._host.model_id),
            hard_pressure_tokens=_hard_pressure_threshold_for_model(self._host.model_id),
        )

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
        del system_prompt, tools
        result = PrepareRequestResult()
        turn_number = completed_turns + 1

        if not chat_local_compaction_enabled():
            if turn_number > 2 and not self._compaction_unavailable_traced:
                self._compaction_unavailable_traced = True
                result.trace_events.append(
                    ProviderTraceEvent(
                        event_type="compaction_skipped",
                        payload={
                            "reason": "chat_completions_no_api_compaction",
                            "model_id": self._host.model_id,
                            "turn_before_request": completed_turns,
                        },
                    )
                )
            return result

        if consecutive_compile_failure_count <= 0 or not last_compile_failure_sig:
            self._last_soft_compaction_failure_sig = None

        if turn_number <= 2:
            return result

        prompt_tokens = self._last_prompt_tokens()
        hard_threshold = _hard_pressure_threshold_for_model(self._host.model_id)
        if (
            hard_threshold is None
            and prompt_tokens is not None
            and not self._unsupported_threshold_event_emitted
        ):
            self._unsupported_threshold_event_emitted = True
            result.trace_events.append(
                ProviderTraceEvent(
                    event_type="compaction_skipped",
                    payload={
                        "reason": "unsupported_threshold_model",
                        "model_id": self._host.model_id,
                        "prompt_tokens": prompt_tokens,
                        "turn_before_request": completed_turns,
                    },
                )
            )

        immutable_end, raw_tail_start = partition_chat_messages(messages)
        compactable_count = max(0, raw_tail_start - immutable_end)
        decision = decide_compaction(
            prompt_tokens=prompt_tokens,
            cached_tokens=self._last_cached_tokens(),
            hard_threshold=hard_threshold,
            consecutive_compile_failure_count=consecutive_compile_failure_count,
            last_compile_failure_sig=last_compile_failure_sig,
            last_soft_compaction_failure_sig=self._last_soft_compaction_failure_sig,
            compactable_item_count=compactable_count,
            turn_number=turn_number,
            last_soft_compaction_turn_number=self._last_soft_compaction_turn_number,
            last_soft_compaction_prompt_tokens=self._last_soft_compaction_prompt_tokens,
        )
        trigger = decision.trigger
        if trigger is None:
            if consecutive_compile_failure_count > 0 and last_compile_failure_sig:
                result.trace_events.append(
                    ProviderTraceEvent(
                        event_type="compaction_skipped",
                        payload={
                            "reason": decision.reason,
                            "model_id": self._host.model_id,
                            "prompt_tokens": prompt_tokens,
                            "cached_tokens": self._last_cached_tokens(),
                            "turn_before_request": completed_turns,
                            "failure_streak": consecutive_compile_failure_count,
                            "pressure_ratio": decision.pressure_ratio,
                            "cache_ratio": decision.cache_ratio,
                            "soft_failure_threshold": decision.soft_failure_threshold,
                            "min_compactable_items": decision.min_compactable_items,
                            "hard_trigger_tokens": decision.hard_trigger_tokens,
                            "compaction_mode": "local_tail",
                        },
                    )
                )
            return result

        if compactable_count <= 0:
            result.trace_events.append(
                ProviderTraceEvent(
                    event_type="compaction_skipped",
                    payload={
                        "reason": "nothing_to_compact",
                        "model_id": self._host.model_id,
                        "turn_before_request": completed_turns,
                        "compaction_mode": "local_tail",
                    },
                )
            )
            return result

        before_chars, after_chars, compacted_count = compact_chat_messages_in_place(
            messages,
            immutable_end=immutable_end,
            raw_tail_start=raw_tail_start,
            max_tool_chars=max_tool_chars_from_env(),
            read_file_max_chars=read_file_max_chars_from_env(),
        )
        if compacted_count <= 0:
            result.trace_events.append(
                ProviderTraceEvent(
                    event_type="compaction_skipped",
                    payload={
                        "reason": "no_oversized_tool_output",
                        "model_id": self._host.model_id,
                        "turn_before_request": completed_turns,
                        "compaction_mode": "local_tail",
                    },
                )
            )
            return result

        estimated_saved = max(0, (before_chars - after_chars) // 4)
        self._last_compaction_turn_number = turn_number
        if trigger == "compile_plateau" and last_compile_failure_sig:
            self._last_soft_compaction_failure_sig = last_compile_failure_sig
            self._last_soft_compaction_turn_number = turn_number
            self._last_soft_compaction_prompt_tokens = prompt_tokens

        result.compaction_event = CompactionEvent(
            turn_before_request=completed_turns,
            trigger=f"local_{trigger}",
            model_id=self._host.model_id,
            usage=None,
            before_next_input_tokens=prompt_tokens,
            after_next_input_tokens=None,
            estimated_saved_next_input_tokens=estimated_saved,
            before_item_count=compactable_count,
            after_item_count=compactable_count,
            previous_response_id_cleared=False,
            guardrails={
                "compaction_mode": "local_tail",
                "compacted_tool_messages": compacted_count,
                "before_chars": before_chars,
                "after_chars": after_chars,
            },
        )
        result.trace_events.append(
            ProviderTraceEvent(
                event_type="compaction",
                payload=result.compaction_event.to_dict(),
            )
        )
        return result

    async def generate_with_tools(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
    ) -> dict[str, Any]:
        if self._host._client is None:
            raise RuntimeError("OpenAI transport is unavailable in dry_run mode")

        request_payload = self._build_chat_payload(
            system_prompt=system_prompt,
            messages=messages,
            tools=tools,
        )

        async def _request_once() -> Any:
            request_coro = self._chat_completion(request_payload)
            timeout = self._host.request_timeout_seconds
            if timeout and timeout > 0:
                return await asyncio.wait_for(request_coro, timeout=float(timeout))
            return await request_coro

        try:
            response = await _async_retry(
                _request_once,
                max_attempts=self._host.max_attempts,
                should_retry=_should_retry_openai_exception,
                base_delay=self._host.retry_base_seconds,
                max_delay=self._host.retry_max_seconds,
                logger=logger,
                context="openai[chat.completions]",
            )
        except Exception as exc:
            if (
                _chat_reasoning_mode() == "auto"
                and self._reasoning_extra_body_supported is not False
                and request_payload.get("extra_body")
                and _is_chat_reasoning_extra_body_unsupported_error(exc)
            ):
                self._reasoning_extra_body_supported = False
                if not self._reasoning_probe_traced:
                    self._reasoning_probe_traced = True
                    logger.info(
                        "OpenAI chat reasoning extra_body unsupported; falling back to none "
                        "(model=%s)",
                        self._host.model_id,
                    )
                retry_payload = self._build_chat_payload(
                    system_prompt=system_prompt,
                    messages=messages,
                    tools=tools,
                )
                retry_payload.pop("extra_body", None)

                async def _retry_without_reasoning() -> Any:
                    request_coro = self._chat_completion(retry_payload)
                    timeout = self._host.request_timeout_seconds
                    if timeout and timeout > 0:
                        return await asyncio.wait_for(request_coro, timeout=float(timeout))
                    return await request_coro

                response = await _async_retry(
                    _retry_without_reasoning,
                    max_attempts=self._host.max_attempts,
                    should_retry=_should_retry_openai_exception,
                    base_delay=self._host.retry_base_seconds,
                    max_delay=self._host.retry_max_seconds,
                    logger=logger,
                    context="openai[chat.completions.no_reasoning]",
                )
            else:
                raise
        else:
            if _chat_reasoning_mode() == "auto" and request_payload.get("extra_body"):
                self._reasoning_extra_body_supported = True

        converted = self._convert_response(response)
        usage = converted.get("usage")
        if isinstance(usage, dict):
            self._last_usage = usage
        return converted

    async def close(self) -> None:
        return None

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
        chat_messages.extend(chat_codec.convert_chat_messages(messages))

        payload: dict[str, Any] = {
            "model": self._host.model_id,
            "messages": chat_messages,
            "tool_choice": "auto",
        }
        converted_tools = chat_codec.convert_tools_for_chat(tools)
        if converted_tools:
            payload["tools"] = converted_tools

        reasoning_extra_body = _reasoning_extra_body(
            self._host.thinking_level,
            reasoning_extra_body_supported=self._reasoning_extra_body_supported,
        )
        if reasoning_extra_body is not None:
            payload["extra_body"] = copy.deepcopy(reasoning_extra_body)

        if self._host.prompt_cache_key:
            payload["prompt_cache_key"] = self._host.prompt_cache_key
            payload["prompt_cache_retention"] = self._host.prompt_cache_retention or "24h"

        return payload

    async def _chat_completion(self, request_payload: dict[str, Any]) -> Any:
        payload = dict(request_payload)
        extra_body = payload.pop("extra_body", None)
        client = self._host._client
        if self._host._client_is_async:
            if extra_body is None:
                return await client.chat.completions.create(**payload)
            return await client.chat.completions.create(**payload, extra_body=extra_body)
        if extra_body is None:
            return await asyncio.to_thread(client.chat.completions.create, **payload)
        return await asyncio.to_thread(
            client.chat.completions.create,
            **payload,
            extra_body=extra_body,
        )

    def _convert_response(self, response: Any) -> dict[str, Any]:
        choice = chat_codec.first_choice(response)
        message = _field(choice, "message")
        if message is None:
            return {}

        content = _field(message, "content")
        tool_calls = chat_codec.serialize_tool_calls(_field(message, "tool_calls"))
        usage = chat_codec.extract_chat_usage(response)

        result: dict[str, Any] = {
            "content": content if isinstance(content, str) else "",
            "tool_calls": tool_calls,
        }
        if usage:
            result["usage"] = usage
            if self._host.prompt_cache_key and not usage.get("cached_tokens"):
                logger.info(
                    "OpenAI chat prompt cache key set but response had no cached_tokens "
                    "(model=%s)",
                    self._host.model_id,
                )
        return result

    def _last_prompt_tokens(self) -> int | None:
        if not isinstance(self._last_usage, dict):
            return None
        prompt_tokens = self._last_usage.get("prompt_tokens")
        return prompt_tokens if isinstance(prompt_tokens, int) else None

    def _last_cached_tokens(self) -> int | None:
        if not isinstance(self._last_usage, dict):
            return None
        cached_tokens = self._last_usage.get("cached_tokens")
        return cached_tokens if isinstance(cached_tokens, int) else None
