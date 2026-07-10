"""Canonical text encoding for agent-authored workspace files."""

from __future__ import annotations

from pathlib import Path

import aiofiles

TEXT_FILE_ENCODING = "utf-8"


def read_text_path(path: Path | str) -> str:
    return Path(path).read_text(encoding=TEXT_FILE_ENCODING)


def write_text_path(path: Path | str, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding=TEXT_FILE_ENCODING)


async def read_text_file(path: Path | str) -> str:
    async with aiofiles.open(path, mode="r", encoding=TEXT_FILE_ENCODING) as file:
        return await file.read()


async def write_text_file(path: Path | str, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(target, mode="w", encoding=TEXT_FILE_ENCODING) as file:
        await file.write(text)
