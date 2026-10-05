from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from RAG.chunking import SplitConfig, build_chunks, load_corpus
from RAG.contextualize import GeneratedContext, build_prompt, contextualize_chunks


class FakeProvider:
    model = "fake"

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, system: str, prompt: str) -> GeneratedContext:
        self.prompts.append(prompt)
        return GeneratedContext("该段说明操作时点。", 100, 15, self.model)


class ContextualizeTests(unittest.TestCase):
    def test_full_parent_prompt_and_resumable_cache(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "rules.md").write_text("# 规则\n\n先检查时点。\n\n再检查对象。\n", encoding="utf-8")
            docs = load_corpus(root)
            chunks = build_chunks(docs, SplitConfig(target_tokens=12, max_tokens=30, overlap_tokens=3))
            provider = FakeProvider()
            cache = root / "cache.jsonl"
            first, report = contextualize_chunks(chunks, docs, provider, cache, 1.0, max_calls=1)
            self.assertEqual(len(first), 1)
            self.assertEqual(report["stop_reason"], "max_calls")
            self.assertIn(docs[0].body, provider.prompts[0])
            self.assertIn(chunks[0]["raw_text"], provider.prompts[0])
            second, report = contextualize_chunks(chunks, docs, provider, cache, 1.0)
            self.assertEqual(len(second), len(chunks))
            self.assertEqual(report["cache_hits"], 1)
            self.assertEqual(second[0]["retrieval_text"], second[0]["context_text"] + "\n\n" + chunks[0]["raw_text"])
            _, report = contextualize_chunks(chunks, docs, provider, cache, 1.0)
            self.assertEqual(report["new_api_calls"], 0)
            self.assertEqual(report["cache_hits"], len(chunks))

    def test_changed_source_and_budget_stop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "rules.md"
            source.write_text("# 规则\n\n检查时点。\n", encoding="utf-8")
            docs = load_corpus(root)
            chunks = build_chunks(docs)
            provider = FakeProvider()
            records, report = contextualize_chunks(chunks, docs, provider, root / "cache.jsonl", 0.000001)
            self.assertEqual(records, [])
            self.assertEqual(report["stop_reason"], "max_cost_usd")
            self.assertEqual(provider.prompts, [])
            source.write_text("# 规则\n\n检查对象。\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source changed"):
                build_prompt(chunks[0], load_corpus(root)[0])


if __name__ == "__main__":
    unittest.main()
