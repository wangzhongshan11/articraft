"""OpenAI API surface normalization and provider option validation."""

from __future__ import annotations

import os
from typing import Literal

from agent.providers.openai_edit_mode import (
    validate_openai_chat_edit_tools,
)

__all__ = [
    "OpenAIApiSurface",
    "classify_provider_failure_kind",
    "normalize_openai_api_surface",
    "openai_compaction_mode",
    "resolve_openai_api_from_provenance",
    "resolve_openai_api_surface",
    "resolve_openai_generation_options",
    "validate_openai_chat_edit_tools",
    "validate_openai_chat_transport",
    "validate_openai_provider_options",
]
from articraft.values import ProviderName, normalize_provider_name

OpenAIApiSurface = Literal["responses", "chat_completions"]

_OPENAI_API_SURFACE_ALIASES: dict[str, OpenAIApiSurface] = {
    "": "responses",
    "responses": "responses",
    "response": "responses",
    "chat": "chat_completions",
    "chat_completions": "chat_completions",
    "completions": "chat_completions",
    "chat-completions": "chat_completions",
}

_OPENAI_API_SURFACE_ENV_KEYS = (
    "ARTICRAFT_OPENAI_API_SURFACE",
    "OPENAI_API_SURFACE",
    "CAD_OPENAI_API_SURFACE",
)


def normalize_openai_api_surface(value: str | None) -> OpenAIApiSurface:
    normalized = (value or "").strip().lower()
    try:
        return _OPENAI_API_SURFACE_ALIASES[normalized]
    except KeyError as exc:
        raise ValueError(f"Unsupported openai_api surface: {value!r}") from exc


def resolve_openai_api_surface(
    *,
    cli_value: str | None = None,
    env: dict[str, str] | None = None,
) -> OpenAIApiSurface:
    if cli_value is not None and str(cli_value).strip():
        return normalize_openai_api_surface(cli_value)

    values = os.environ if env is None else env
    for key in _OPENAI_API_SURFACE_ENV_KEYS:
        raw = values.get(key)
        if raw and str(raw).strip():
            return normalize_openai_api_surface(raw)
    return "responses"


def validate_openai_chat_transport(
    openai_api: str | OpenAIApiSurface,
    openai_transport: str,
) -> None:
    api = normalize_openai_api_surface(openai_api)
    transport = (openai_transport or "http").strip().lower()
    if api == "chat_completions" and transport == "websocket":
        raise ValueError(
            "openai_api=chat_completions does not support openai_transport=websocket."
        )


def openai_compaction_mode(openai_api: str | OpenAIApiSurface) -> str:
    if normalize_openai_api_surface(openai_api) == "chat_completions":
        from agent.providers.chat_local_compaction import chat_local_compaction_enabled

        return "local_tail" if chat_local_compaction_enabled() else "none"
    return "api_responses_only"


def resolve_openai_api_from_provenance(generation: dict[str, object] | None) -> str:
    if not isinstance(generation, dict):
        return "responses"
    stored = generation.get("openai_api")
    if isinstance(stored, str) and stored.strip():
        return normalize_openai_api_surface(stored)
    return "responses"


def resolve_openai_generation_options(
    *,
    provider: str,
    openai_api_cli: str | None = None,
    openai_transport: str = "http",
) -> tuple[str, str]:
    api = validate_openai_provider_options(
        provider=provider,
        openai_api=resolve_openai_api_surface(cli_value=openai_api_cli),
        openai_transport=openai_transport,
        cli_openai_api=openai_api_cli,
    )
    transport = (openai_transport or "http").strip().lower()
    return api, transport


def classify_provider_failure_kind(*, status: str, message: str | None) -> str | None:
    if status == "success":
        return None
    text = (message or "").strip().lower()
    if not text:
        return "unknown"
    if "504" in text or "gateway timeout" in text:
        return "http_504"
    if any(token in text for token in ("502", "503", "500")):
        return "http_5xx"
    if "400" in text or "422" in text or "bad request" in text:
        return "http_4xx"
    if "connection" in text or "timeout" in text or "timed out" in text:
        return "connection"
    if "cost limit" in text:
        return "cost_limit"
    if "compile" in text:
        return "compile"
    return "other"


def validate_openai_provider_options(
    *,
    provider: str,
    openai_api: str | OpenAIApiSurface,
    openai_transport: str,
    cli_openai_api: str | None = None,
    env: dict[str, str] | None = None,
) -> OpenAIApiSurface:
    api = normalize_openai_api_surface(openai_api)
    provider_norm = normalize_provider_name(provider)
    if provider_norm is not ProviderName.OPENAI:
        if cli_openai_api is not None:
            raise ValueError(
                f"--openai-api is only supported for provider openai "
                f"(got provider={provider!r}, openai_api={api!r})."
            )
        return "responses"

    validate_openai_chat_transport(api, openai_transport)
    validate_openai_chat_edit_tools(api, env=env)
    return api
