"""Measure first-turn context document sizes."""

from __future__ import annotations

import json
from pathlib import Path

from agent.prompts import load_sdk_docs_reference, load_system_prompt_text
from agent.tools import (
    build_first_turn_messages,
    build_first_turn_runtime_guidance,
    build_tool_registry,
)
from agent.workspace_docs import load_sdk_docs_bundle


def chars(text: str) -> int:
    return len(text)


def words(text: str) -> int:
    return len(text.split())


def lines(text: str) -> int:
    return text.count("\n") + 1


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    providers = ["openai", "gemini", "anthropic", "openrouter"]

    print("=== SYSTEM PROMPT ===")
    for provider in providers:
        path, text = load_system_prompt_text(
            "designer_system_prompt.txt",
            provider=provider,
            sdk_package="sdk",
            repo_root=repo,
        )
        print(
            f"{provider}: file={path.name} chars={chars(text):,} "
            f"words={words(text):,} lines={lines(text)}"
        )

    print("\n=== PRELOADED SDK DOCS (sdk_docs_context) ===")
    docs = load_sdk_docs_reference(repo, sdk_package="sdk")
    print(f"total chars={chars(docs):,} words={words(docs):,} lines={lines(docs)}")
    bundle = load_sdk_docs_bundle(repo, sdk_package="sdk")
    for virtual_path in bundle.default_read_virtual_paths():
        text = bundle.read_text(virtual_path)
        print(
            f"  {virtual_path}: chars={chars(text):,} words={words(text):,} "
            f"lines={lines(text)}"
        )

    print("\n=== RUNTIME GUIDANCE ===")
    guidance = build_first_turn_runtime_guidance("openai")
    print(f"chars={chars(guidance):,} words={words(guidance):,}")

    print("\n=== SAMPLE USER MESSAGES ===")
    sample_prompt = "A yellow motor grader with articulated blade."
    conversation = build_first_turn_messages(
        sample_prompt,
        sdk_docs_context=docs,
        provider="openai",
    )
    for index, message in enumerate(conversation):
        content = message["content"]
        if isinstance(content, str):
            size = chars(content)
        else:
            size = sum(
                len(part.get("text", "")) for part in content if isinstance(part, dict)
            )
        print(f"message[{index}] role={message['role']} chars={size:,}")

    print("\n=== TOOL SCHEMAS ===")
    for provider in providers:
        tools = build_tool_registry(provider, sdk_package="sdk").get_tool_schemas()
        blob = json.dumps(tools, ensure_ascii=False)
        print(f"{provider}: tools={len(tools)} schema_json_chars={chars(blob):,}")

    print("\n=== ALL VIRTUAL DOCS (read_file, not preloaded) ===")
    all_docs = bundle.files_by_path
    print(f"virtual_files={len(all_docs)}")
    sizes = [(virtual_path, chars(file.read_text())) for virtual_path, file in sorted(all_docs.items())]
    print(f"total_if_all_loaded chars={sum(size for _, size in sizes):,}")
    for virtual_path, size in sizes:
        print(f"  {virtual_path}: {size:,}")

    print("\n=== PROMPT SECTIONS (source markdown) ===")
    sections_dir = repo / "agent" / "prompts" / "sections"
    for path in sorted(sections_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        print(f"  {path.name}: chars={chars(text):,} lines={lines(text)}")

    scaffold = (repo / "scaffold.py").read_text(encoding="utf-8")
    print("\n=== INITIAL model.py (scaffold) ===")
    print(f"chars={chars(scaffold):,} lines={lines(scaffold)}")

    print("\n=== FIRST TURN TOTAL (openai, text-only prompt) ===")
    _, system_prompt = load_system_prompt_text(
        "designer_system_prompt.txt",
        provider="openai",
        sdk_package="sdk",
        repo_root=repo,
    )
    tools = build_tool_registry("openai").get_tool_schemas()
    tool_blob = json.dumps(tools, ensure_ascii=False)
    user_total = 0
    for message in conversation:
        content = message["content"]
        if isinstance(content, str):
            user_total += chars(content)
        else:
            user_total += sum(
                len(part.get("text", "")) for part in content if isinstance(part, dict)
            )
    grand_total = chars(system_prompt) + user_total + chars(tool_blob)
    print(f"system_prompt={chars(system_prompt):,}")
    print(f"user_messages={user_total:,}")
    print(f"tool_schemas={chars(tool_blob):,}")
    print(f"grand_total_chars={grand_total:,}")
    print(f"approx_tokens_div4={grand_total // 4:,}")


if __name__ == "__main__":
    main()
