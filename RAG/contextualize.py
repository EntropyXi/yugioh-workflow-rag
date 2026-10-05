from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from RAG.chunking import SourceDocument, canonical_json, sha256_text, token_count


PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "context_v1.txt"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
PRICE_REFERENCE = "https://api-docs.deepseek.com/quick_start/pricing/"
PEAK_INPUT_USD_PER_MILLION = 0.30
PEAK_OUTPUT_USD_PER_MILLION = 1.20
MAX_OUTPUT_TOKENS = 128


@dataclass(frozen=True)
class GeneratedContext:
    text: str
    input_tokens: int
    output_tokens: int
    returned_model: str


class ContextProvider(Protocol):
    model: str

    def generate(self, system: str, prompt: str) -> GeneratedContext: ...


class DeepSeekProvider:
    def __init__(self, model: str = "deepseek-flash", api_key: str | None = None,
                 timeout_seconds: int = 90) -> None:
        self.model = model
        self._api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self._api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set")
        self.timeout_seconds = timeout_seconds

    def generate(self, system: str, prompt: str) -> GeneratedContext:
        payload = {
            "model": self.model,
            "max_tokens": MAX_OUTPUT_TOKENS,
            "temperature": 0,
            "thinking": {"type": "disabled"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        request = urllib.request.Request(
            DEEPSEEK_URL,
            data=canonical_json(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                data = json.load(response)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"DeepSeek API returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DeepSeek API connection failed: {exc.reason}") from exc
        choice = data["choices"][0]
        if choice.get("finish_reason") != "stop":
            raise RuntimeError(f"DeepSeek response stopped with {choice.get('finish_reason')!r}")
        text = choice["message"].get("content") or ""
        usage = data.get("usage") or {}
        if not text.strip():
            raise RuntimeError("DeepSeek returned empty context")
        if not isinstance(usage.get("prompt_tokens"), int) or not isinstance(usage.get("completion_tokens"), int):
            raise RuntimeError("DeepSeek response is missing token usage")
        return GeneratedContext(
            text=text.strip(),
            input_tokens=usage["prompt_tokens"],
            output_tokens=usage["completion_tokens"],
            returned_model=str(data.get("model") or self.model),
        )


def load_prompt(path: Path = PROMPT_PATH) -> tuple[str, str]:
    system = path.read_text(encoding="utf-8").strip()
    if not system:
        raise ValueError("context prompt is empty")
    return system, sha256_text(system)


def build_prompt(chunk: dict[str, Any], document: SourceDocument) -> str:
    if document.source_path != chunk["source_path"] or document.source_sha256 != chunk["source_sha256"]:
        raise ValueError(f"source changed after chunking: {chunk['source_path']}")
    raw = document.raw[chunk["source_start_char"]:chunk["source_end_char"]]
    parent = document.raw[chunk["parent_start_char"]:chunk["parent_end_char"]]
    if raw != chunk["raw_text"] or sha256_text(parent) != chunk["parent_sha256"]:
        raise ValueError(f"chunk or parent span does not match source: {chunk['chunk_id']}")
    title = str(document.metadata.get("title") or Path(document.source_path).stem)
    heading = " > ".join(chunk["heading_path"]) or "文档开头"
    return (
        f"<source_path>{document.source_path}</source_path>\n"
        f"<source_tier>{chunk['source_tier']}</source_tier>\n"
        f"<document_title>{title}</document_title>\n"
        f"<heading_path>{heading}</heading_path>\n"
        f"<parent_scope>{chunk['parent_scope']}</parent_scope>\n"
        f"<document>\n{parent}\n</document>\n"
        f"<chunk>\n{raw}\n</chunk>"
    )


def cache_key(chunk: dict[str, Any], model: str, prompt_sha256: str) -> str:
    identity = {
        "chunk_id": chunk["chunk_id"],
        "source_sha256": chunk["source_sha256"],
        "parent_sha256": chunk["parent_sha256"],
        "prompt_sha256": prompt_sha256,
        "model": model,
    }
    return sha256_text(canonical_json(identity))


def read_cache(path: Path) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return entries
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"blank cache line at {path}:{line_number}")
        entry = json.loads(line)
        key = entry["cache_key"]
        if key in entries and entries[key] != entry:
            raise ValueError(f"conflicting cache entry for {key}")
        entries[key] = entry
    return entries


def _append_cache(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as file:
        file.write(canonical_json(entry) + "\n")
        file.flush()
        os.fsync(file.fileno())


def worst_case_cost_usd(input_tokens: int, output_tokens: int = MAX_OUTPUT_TOKENS) -> float:
    return ((input_tokens * PEAK_INPUT_USD_PER_MILLION)
            + (output_tokens * PEAK_OUTPUT_USD_PER_MILLION)) / 1_000_000


def contextualize_chunks(
    chunks: list[dict[str, Any]],
    documents: list[SourceDocument],
    provider: ContextProvider,
    cache_path: Path,
    max_cost_usd: float,
    max_calls: int | None = None,
    prompt_path: Path = PROMPT_PATH,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if max_cost_usd <= 0:
        raise ValueError("max_cost_usd must be positive")
    if max_calls is not None and max_calls <= 0:
        raise ValueError("max_calls must be positive")
    system, prompt_sha = load_prompt(prompt_path)
    sources = {document.source_path: document for document in documents}
    cache = read_cache(cache_path)
    prior_cost = sum(
        worst_case_cost_usd(entry["input_tokens"], entry["output_tokens"])
        for entry in cache.values()
    )
    results: list[dict[str, Any]] = []
    calls = 0
    hits = 0
    actual_cost = 0.0
    input_tokens = 0
    output_tokens = 0
    stop_reason: str | None = None
    for chunk in chunks:
        document = sources.get(chunk["source_path"])
        if document is None:
            raise ValueError(f"missing source document: {chunk['source_path']}")
        prompt = build_prompt(chunk, document)
        key = cache_key(chunk, provider.model, prompt_sha)
        entry = cache.get(key)
        if entry is None:
            if max_calls is not None and calls >= max_calls:
                stop_reason = "max_calls"
                break
            reserved_input = len((system + prompt).encode("utf-8")) + 512
            reserve = worst_case_cost_usd(reserved_input)
            if prior_cost + actual_cost + reserve > max_cost_usd:
                stop_reason = "max_cost_usd"
                break
            generated = provider.generate(system, prompt)
            calls += 1
            entry = {
                "cache_key": key,
                "context_text": generated.text,
                "context_tokens_estimated": token_count(generated.text),
                "input_tokens": generated.input_tokens,
                "output_tokens": generated.output_tokens,
                "returned_model": generated.returned_model,
                "prompt_sha256": prompt_sha,
            }
            _append_cache(cache_path, entry)
            cache[key] = entry
            actual_cost += worst_case_cost_usd(generated.input_tokens, generated.output_tokens)
            input_tokens += generated.input_tokens
            output_tokens += generated.output_tokens
        else:
            hits += 1
        if not entry["context_text"].strip():
            raise ValueError(f"empty cached context: {key}")
        context = entry["context_text"].strip()
        results.append({
            **chunk,
            "context_text": context,
            "context_tokens_estimated": entry["context_tokens_estimated"],
            "retrieval_text": context + "\n\n" + chunk["raw_text"],
            "context_model": provider.model,
            "context_returned_model": entry["returned_model"],
            "context_prompt_sha256": prompt_sha,
            "context_cache_key": key,
        })
    report = {
        "total_chunks": len(chunks),
        "completed_chunks": len(results),
        "cache_hits": hits,
        "new_api_calls": calls,
        "input_tokens_new_calls": input_tokens,
        "output_tokens_new_calls": output_tokens,
        "peak_price_estimate_usd": round(actual_cost, 8),
        "prior_cache_peak_price_estimate_usd": round(prior_cost, 8),
        "cumulative_peak_price_estimate_usd": round(prior_cost + actual_cost, 8),
        "max_cost_usd": max_cost_usd,
        "price_reference": PRICE_REFERENCE,
        "stop_reason": stop_reason,
        "model": provider.model,
        "prompt_sha256": prompt_sha,
    }
    return results, report
