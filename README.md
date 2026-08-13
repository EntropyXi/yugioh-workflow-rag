# Yu-Gi-Oh! Operation Legality Judgment Dataset

> An open-source, non-commercial dataset and RAG research project for source-grounded Yu-Gi-Oh! ruling evaluation.

This project defines structured cases for judging whether a proposed operation or effect resolution is legal under the relevant rules, given a known game state. It does not recommend plays, build decks, simulate complete duels, or perform strategic analysis.

## Implemented

- A JSONL case format, documented schema, fixed v1 enums, and case templates.
- Chain/zone/column mapping rules and manually curated Ash Blossom and Infinite Impermanence cases.

## Planned Retrieval Knowledge Base

Future work is intended to use official ruling and rule materials as a source-grounded retrieval corpus:
```text
official Q&A / rule documents -> parsing and chunking -> embeddings and metadata -> retrieval -> ruling judgments
```
Large-scale collection has not been implemented. The project is seeking guidance on appropriate access and permitted use.

## Not Implemented Yet

- A 10-case seed set and 50 human-verified gold cases.
- An official knowledge base, retrieval, knowledge graph, RAG pipeline, and evaluation metrics.

## Disclaimer

This is an unofficial research project, not affiliated with, endorsed by, or sponsored by KONAMI.
Yu-Gi-Oh! and related official materials belong to their respective rights holders. This repository does not contain or redistribute a bulk copy of KONAMI's official Q&A database or rule documents.

Key files: `schema.md`, `cases_json模板.md`, `gpt_to_codex/operation_legality_cases.jsonl`, and `ygo_json_case_changelog.md`.
