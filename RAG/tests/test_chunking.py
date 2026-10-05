from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from RAG.agent import check_body_coverage
from RAG.chunking import SplitConfig, build_chunks, load_corpus, sha256_text, token_count


class ChunkingTests(unittest.TestCase):
    def test_deterministic_offsets_and_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "nested").mkdir()
            source = root / "nested" / "rules.md"
            source.write_text(
                "---\ndoc_id: local_rule\ntitle: 示例\n---\n\n"
                "# 总则\n\n第一段。\n\n## 时点\n\n第二段。\n\n```text\n# not a heading\n```\n",
                encoding="utf-8",
            )
            documents = load_corpus(root)
            config = SplitConfig(target_tokens=20, max_tokens=40, overlap_tokens=5)
            first = build_chunks(documents, config)
            second = build_chunks(load_corpus(root), config)
            self.assertEqual(first, second)
            self.assertEqual({item["source_path"] for item in first}, {"nested/rules.md"})
            self.assertEqual({item["doc_id"] for item in first}, {"local_rule"})
            check_body_coverage(documents, first)
            raw = documents[0].raw
            for item in first:
                self.assertEqual(raw[item["source_start_char"]:item["source_end_char"]], item["raw_text"])
                self.assertEqual(
                    sha256_text(raw[item["parent_start_char"]:item["parent_end_char"]]),
                    item["parent_sha256"],
                )
                self.assertLessEqual(token_count(item["raw_text"]), config.max_tokens)
                self.assertEqual(item["source_tier"], "secondary_reference")

    def test_large_paragraph_is_split_without_content_loss(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "large.md").write_text("# 标题\n\n" + "操作合法。" * 180, encoding="utf-8")
            documents = load_corpus(root)
            chunks = build_chunks(documents, SplitConfig(target_tokens=50, max_tokens=70, overlap_tokens=10))
            self.assertGreater(len(chunks), 2)
            check_body_coverage(documents, chunks)
            self.assertTrue(all(item["token_count"] <= 70 for item in chunks))


if __name__ == "__main__":
    unittest.main()
