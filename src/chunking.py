"""Markdown chunking with overlap for RAG ingest."""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterator


@dataclass
class Chunk:
    chunk_id: str
    source: str
    text: str
    start_char: int
    end_char: int
    section: str

    def to_dict(self) -> dict:
        return asdict(self)


def _split_markdown_sections(text: str) -> list[tuple[str, str]]:
    """Split on AT/## headings; return (section_title, body) pairs."""
    lines = text.splitlines(keepends=True)
    sections: list[tuple[str, str]] = []
    current_title = "Introduction"
    current_body: list[str] = []

    heading_re = re.compile(r"^(#{1,3})\s+(.+?)\s*$")

    for line in lines:
        m = heading_re.match(line.strip("\n"))
        if m:
            body = "".join(current_body).strip()
            if body:
                sections.append((current_title, body))
            current_title = m.group(2).strip()
            current_body = []
        else:
            current_body.append(line)

    body = "".join(current_body).strip()
    if body:
        sections.append((current_title, body))

    if not sections and text.strip():
        sections.append(("Document", text.strip()))

    return sections


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> list[Chunk]:
    """
    Chunk by characters with overlap, preferring section boundaries.

    chunk_size / chunk_overlap are in characters (portfolio-scale, CPU-friendly).
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    sections = _split_markdown_sections(text)
    chunks: list[Chunk] = []
    global_offset = 0
    counter = 0

    # Approximate char offsets by scanning original text once for titles
    for section_title, body in sections:
        start = 0
        body_len = len(body)
        while start < body_len:
            end = min(start + chunk_size, body_len)
            piece = body[start:end].strip()
            if piece:
                chunk_id = f"{Path(source).stem}::{counter:03d}"
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        source=source,
                        text=piece,
                        start_char=global_offset + start,
                        end_char=global_offset + end,
                        section=section_title,
                    )
                )
                counter += 1
            if end >= body_len:
                break
            start = max(0, end - chunk_overlap)
        global_offset += body_len + 1

    return chunks


def load_markdown_files(data_dir: Path) -> Iterator[tuple[str, str]]:
    """Yield (filename, text) for each .md file in data_dir."""
    paths = sorted(data_dir.glob("*.md"))
    for path in paths:
        yield path.name, path.read_text(encoding="utf-8")


def chunk_corpus(
    data_dir: Path,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> list[Chunk]:
    all_chunks: list[Chunk] = []
    for name, text in load_markdown_files(data_dir):
        all_chunks.extend(
            chunk_text(text, source=name, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        )
    return all_chunks
