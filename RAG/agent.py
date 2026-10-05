from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

from RAG.chunking import (
    ALGORITHM_VERSION,
    CORPUS_DIR,
    TOKENIZER_NAME,
    SplitConfig,
    build_chunks,
    canonical_json,
    load_corpus,
    write_jsonl,
)
from RAG.contextualize import DeepSeekProvider, contextualize_chunks


ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"


def check_body_coverage(documents: list, chunks: list[dict]) -> None:
    by_source: dict[str, list[dict]] = {}
    for chunk in chunks:
        by_source.setdefault(chunk["source_path"], []).append(chunk)
    for document in documents:
        parts = sorted(by_source.get(document.source_path, []), key=lambda item: item["core_start_char"])
        cursor = document.body_offset
        for part in parts:
            if part["core_start_char"] < cursor or document.raw[cursor:part["core_start_char"]].strip():
                raise ValueError(f"chunk coverage gap/overlap in {document.source_path} at {cursor}")
            if part["core_end_char"] <= cursor:
                raise ValueError(f"empty core in {document.source_path} at {cursor}")
            cursor = part["core_end_char"]
        if document.raw[cursor:].strip():
            raise ValueError(f"chunk coverage incomplete in {document.source_path} at {cursor}")


def command_chunk(args: argparse.Namespace) -> int:
    config = SplitConfig(
        target_tokens=args.target_tokens,
        max_tokens=args.max_tokens,
        overlap_tokens=args.overlap_tokens,
        max_parent_tokens=args.max_parent_tokens,
    )
    documents = load_corpus(args.corpus)
    chunks = build_chunks(documents, config)
    check_body_coverage(documents, chunks)
    digest = write_jsonl(args.output, chunks)
    manifest = {
        "algorithm_version": ALGORITHM_VERSION,
        "corpus_root": str(args.corpus.resolve()),
        "source_count": len(documents),
        "chunk_count": len(chunks),
        "source_sha256": {doc.source_path: doc.source_sha256 for doc in documents},
        "source_tiers": dict(Counter(chunk["source_tier"] for chunk in chunks)),
        "split_config": asdict(config),
        "tokenizer": TOKENIZER_NAME,
        "tiktoken_version": version("tiktoken"),
        "pyyaml_version": version("PyYAML"),
        "chunks_sha256": digest,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(canonical_json(manifest) + "\n", encoding="utf-8", newline="\n")
    print(canonical_json({"source_count": len(documents), "chunk_count": len(chunks), "chunks_sha256": digest}))
    return 0


def command_contextualize(args: argparse.Namespace) -> int:
    chunks = [json.loads(line) for line in args.chunks.read_text(encoding="utf-8").splitlines() if line.strip()]
    documents = load_corpus(args.corpus)
    provider = DeepSeekProvider(model=args.model)
    records, report = contextualize_chunks(
        chunks, documents, provider, args.cache, args.max_cost_usd, args.max_calls
    )
    write_jsonl(args.output, records)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(canonical_json(report) + "\n", encoding="utf-8", newline="\n")
    print(canonical_json(report))
    return 0 if report["completed_chunks"] == report["total_chunks"] else 3


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build traceable Markdown chunks and contextual retrieval text")
    commands = parser.add_subparsers(dest="command", required=True)
    chunk = commands.add_parser("chunk")
    chunk.add_argument("--corpus", type=Path, default=CORPUS_DIR)
    chunk.add_argument("--output", type=Path, default=ARTIFACTS_DIR / "chunks.jsonl")
    chunk.add_argument("--manifest", type=Path, default=ARTIFACTS_DIR / "chunks_manifest.json")
    chunk.add_argument("--target-tokens", type=int, default=400)
    chunk.add_argument("--max-tokens", type=int, default=600)
    chunk.add_argument("--overlap-tokens", type=int, default=50)
    chunk.add_argument("--max-parent-tokens", type=int, default=12000)
    chunk.set_defaults(run=command_chunk)
    context = commands.add_parser("contextualize")
    context.add_argument("--corpus", type=Path, default=CORPUS_DIR)
    context.add_argument("--chunks", type=Path, default=ARTIFACTS_DIR / "chunks.jsonl")
    context.add_argument("--output", type=Path, default=ARTIFACTS_DIR / "contextualized_chunks.jsonl")
    context.add_argument("--cache", type=Path, default=ARTIFACTS_DIR / "context_cache.jsonl")
    context.add_argument("--report", type=Path, default=ARTIFACTS_DIR / "context_report.json")
    context.add_argument("--model", default="deepseek-flash")
    context.add_argument("--max-cost-usd", type=float, required=True)
    context.add_argument("--max-calls", type=int)
    context.set_defaults(run=command_contextualize)
    return parser


def main() -> int:
    args = make_parser().parse_args()
    try:
        return args.run(args)
    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
