from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import tiktoken
import yaml


CORPUS_DIR = Path(__file__).resolve().parent / "docs"
ALGORITHM_VERSION = "markdown-chunks-v1"
TOKENIZER_NAME = "cl100k_base"
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*$")
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")


@dataclass(frozen=True)
class SplitConfig:
    target_tokens: int = 400
    max_tokens: int = 600
    overlap_tokens: int = 50
    max_parent_tokens: int = 12000

    def __post_init__(self) -> None:
        if not (0 <= self.overlap_tokens < self.target_tokens <= self.max_tokens):
            raise ValueError("require 0 <= overlap < target <= max tokens")
        if self.max_parent_tokens < self.max_tokens:
            raise ValueError("max_parent_tokens must be at least max_tokens")


@dataclass(frozen=True)
class SourceDocument:
    source_path: str
    source_sha256: str
    raw: str
    body_offset: int
    metadata: dict[str, Any]

    @property
    def body(self) -> str:
        return self.raw[self.body_offset:]


@dataclass(frozen=True)
class HeadingNode:
    start: int
    end: int
    depth: int
    title: str
    path: tuple[str, ...]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def token_count(value: str) -> int:
    return len(tiktoken.get_encoding(TOKENIZER_NAME).encode(value, disallowed_special=()))


def load_corpus(corpus_root: Path = CORPUS_DIR) -> list[SourceDocument]:
    corpus_root = corpus_root.resolve()
    if not corpus_root.is_dir():
        raise FileNotFoundError(f"corpus directory does not exist: {corpus_root}")
    documents: list[SourceDocument] = []
    for path in sorted(corpus_root.rglob("*.md"), key=lambda p: p.relative_to(corpus_root).as_posix()):
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines(keepends=True)
        metadata: dict[str, Any] = {}
        body_offset = 0
        if lines and lines[0].strip() == "---":
            closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
            if closing is None:
                raise ValueError(f"unclosed YAML frontmatter: {path}")
            parsed = yaml.safe_load("".join(lines[1:closing]))
            if parsed is not None and not isinstance(parsed, dict):
                raise ValueError(f"YAML frontmatter must be an object: {path}")
            metadata = parsed or {}
            body_offset = sum(len(line) for line in lines[:closing + 1])
        if not raw[body_offset:].strip():
            raise ValueError(f"empty Markdown body: {path}")
        documents.append(SourceDocument(
            source_path=path.relative_to(corpus_root).as_posix(),
            source_sha256=sha256_text(raw),
            raw=raw,
            body_offset=body_offset,
            metadata=metadata,
        ))
    if not documents:
        raise ValueError(f"no Markdown files found in {corpus_root}")
    return documents


def _heading_nodes(body: str) -> list[HeadingNode]:
    starts: list[tuple[int, int, str, tuple[str, ...]]] = []
    titles: list[str] = []
    fence: tuple[str, int] | None = None
    position = 0
    for line in body.splitlines(keepends=True):
        fence_match = FENCE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
        elif fence is None:
            heading = HEADING.match(line.rstrip("\r\n"))
            if heading:
                depth = len(heading.group(1))
                title = heading.group(2).strip()
                titles = titles[:depth - 1]
                titles.append(title)
                starts.append((position, depth, title, tuple(titles)))
        position += len(line)
    nodes: list[HeadingNode] = []
    for index, (start, depth, title, path) in enumerate(starts):
        end = next((later[0] for later in starts[index + 1:] if later[1] <= depth), len(body))
        nodes.append(HeadingNode(start, end, depth, title, path))
    return nodes


def _sections(body: str, nodes: list[HeadingNode]) -> list[tuple[int, int, tuple[str, ...]]]:
    if not nodes:
        return [(0, len(body), ())]
    sections: list[tuple[int, int, tuple[str, ...]]] = []
    if nodes[0].start > 0:
        sections.append((0, nodes[0].start, ()))
    for index, node in enumerate(nodes):
        end = nodes[index + 1].start if index + 1 < len(nodes) else len(body)
        sections.append((node.start, end, node.path))
    return sections


def _paragraph_ranges(text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start = 0
    position = 0
    fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        marker = FENCE.match(line)
        if marker:
            sequence = marker.group(1)
            if fence is None:
                fence = (sequence[0], len(sequence))
            elif sequence[0] == fence[0] and len(sequence) >= fence[1]:
                fence = None
        position += len(line)
        if fence is None and not line.strip():
            ranges.append((start, position))
            start = position
    if start < len(text):
        ranges.append((start, len(text)))
    return ranges


def _largest_prefix(text: str, start: int, maximum: int) -> int:
    low, high = start + 1, len(text)
    result = start + 1
    while low <= high:
        middle = (low + high) // 2
        if token_count(text[start:middle]) <= maximum:
            result = middle
            low = middle + 1
        else:
            high = middle - 1
    return result


def _split_large(text: str, start: int, end: int, maximum: int) -> list[tuple[int, int]]:
    parts: list[tuple[int, int]] = []
    while start < end:
        limit = _largest_prefix(text[:end], start, maximum)
        if limit >= end:
            parts.append((start, end))
            break
        window = text[start:limit]
        choices = [match.end() for match in re.finditer(r"\n\n+|\n|[。！？；][ \t]*", window)]
        viable = [candidate for candidate in choices if candidate >= len(window) // 2]
        cut = start + (viable[-1] if viable else len(window))
        if cut <= start:
            raise ValueError("failed to advance while splitting a long paragraph")
        parts.append((start, cut))
        start = cut
    return parts


def _core_ranges(text: str, config: SplitConfig) -> list[tuple[int, int]]:
    units: list[tuple[int, int]] = []
    for start, end in _paragraph_ranges(text):
        if token_count(text[start:end]) <= config.max_tokens:
            units.append((start, end))
        else:
            units.extend(_split_large(text, start, end, config.max_tokens))
    cores: list[tuple[int, int]] = []
    current_start: int | None = None
    current_end = 0
    for start, end in units:
        if current_start is None:
            current_start, current_end = start, end
        elif token_count(text[current_start:end]) <= config.target_tokens:
            current_end = end
        else:
            cores.append((current_start, current_end))
            current_start, current_end = start, end
    if current_start is not None:
        cores.append((current_start, current_end))
    return cores


def _overlap_start(text: str, section_start: int, core_start: int, core_end: int, config: SplitConfig) -> int:
    if core_start <= section_start or config.overlap_tokens == 0:
        return core_start
    low, high = section_start, core_start
    result = core_start
    while low <= high:
        middle = (low + high) // 2
        if (token_count(text[middle:core_start]) <= config.overlap_tokens
                and token_count(text[middle:core_end]) <= config.max_tokens):
            result = middle
            high = middle - 1
        else:
            low = middle + 1
    return result


def _parent_range(body: str, nodes: list[HeadingNode], core_start: int, core_end: int,
                  config: SplitConfig) -> tuple[int, int, str]:
    if token_count(body) <= config.max_parent_tokens:
        return 0, len(body), "document"
    candidates = [node for node in nodes if node.start <= core_start and node.end >= core_end]
    for node in sorted(candidates, key=lambda item: item.depth):
        if token_count(body[node.start:node.end]) <= config.max_parent_tokens:
            return node.start, node.end, f"heading_{node.depth}"
    for node in sorted(candidates, key=lambda item: item.depth, reverse=True):
        next_start = next((later.start for later in nodes if later.start > node.start), len(body))
        if next_start >= core_end and token_count(body[node.start:next_start]) <= config.max_parent_tokens:
            return node.start, next_start, f"heading_block_{node.depth}"
    if HEADING.match(body[core_start:core_end].strip()):
        return core_start, core_end, "heading_only"
    raise ValueError(f"no parent section fits max_parent_tokens at body offset {core_start}; split this source into logical documents")


def build_chunks(documents: list[SourceDocument], config: SplitConfig = SplitConfig()) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    split_config_hash = sha256_text(canonical_json({"version": ALGORITHM_VERSION, **asdict(config)}))
    for document in documents:
        body = document.body
        nodes = _heading_nodes(body)
        chunk_index = 0
        for section_start, section_end, heading_path in _sections(body, nodes):
            section = body[section_start:section_end]
            for core_start, core_end in _core_ranges(section, config):
                core_body_start = section_start + core_start
                core_body_end = section_start + core_end
                start = _overlap_start(section, 0, core_start, core_end, config)
                body_start = section_start + start
                try:
                    parent_start, parent_end, parent_scope = _parent_range(
                        body, nodes, core_body_start, core_body_end, config
                    )
                except ValueError as exc:
                    raise ValueError(f"{document.source_path}: {exc}") from exc
                source_start = document.body_offset + body_start
                source_end = document.body_offset + core_body_end
                core_source_start = document.body_offset + core_body_start
                parent_source_start = document.body_offset + parent_start
                parent_source_end = document.body_offset + parent_end
                raw_text = document.raw[source_start:source_end]
                if not raw_text.strip():
                    continue
                count = token_count(raw_text)
                if count > config.max_tokens:
                    raise ValueError(f"chunk exceeds max_tokens: {document.source_path}:{source_start}")
                identity = {
                    "source_path": document.source_path,
                    "source_sha256": document.source_sha256,
                    "core_start_char": core_source_start,
                    "core_end_char": source_end,
                    "split_config_sha256": split_config_hash,
                }
                chunks.append({
                    "chunk_id": sha256_text(canonical_json(identity))[:24],
                    "chunk_index": chunk_index,
                    "doc_id": str(document.metadata.get("doc_id") or Path(document.source_path).stem),
                    "source_path": document.source_path,
                    "source_sha256": document.source_sha256,
                    "source_tier": "secondary_reference",
                    "metadata": document.metadata,
                    "heading_path": list(heading_path),
                    "source_start_char": source_start,
                    "source_end_char": source_end,
                    "core_start_char": core_source_start,
                    "core_end_char": source_end,
                    "start_line": document.raw.count("\n", 0, source_start) + 1,
                    "end_line": document.raw.count("\n", 0, source_end - 1) + 1,
                    "parent_start_char": parent_source_start,
                    "parent_end_char": parent_source_end,
                    "parent_scope": parent_scope,
                    "parent_sha256": sha256_text(document.raw[parent_source_start:parent_source_end]),
                    "raw_text": raw_text,
                    "token_count": count,
                })
                chunk_index += 1
    identifiers = [chunk["chunk_id"] for chunk in chunks]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("chunk IDs are not unique")
    return chunks


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> str:
    content = "\n".join(canonical_json(record) for record in records) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return sha256_text(content)
