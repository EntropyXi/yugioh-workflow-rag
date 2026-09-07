# YGO Ruling Evaluation Workflow&RAG

> An open-source, non-commercial dataset and RAG research project for source-grounded Yu-Gi-Oh! ruling evaluation.

This project defines structured cases for judging whether a proposed operation or effect resolution is legal under the relevant rules, given a known game state. It does not recommend plays, build decks, simulate complete duels, or perform strategic analysis.

## Implemented

- 58 human-verified gold cases in `gold_cases/operation_legality_cases.jsonl` (one JSON object per line) with formatted mirrors in `gold_cases/json/case001.json`–`case058.json`.
- An executable JSON Schema (`docs/operation_case.schema.json`, v2.1.0, Draft 2020-12) and a two-layer validator (`check_jsonlschema.py`) covering schema rules, project business rules, mirror consistency, and 16 negative self-tests.
- A RAG retrieval evaluation set (`eval/rag_eval_set.jsonl`, 151 queries across easy/medium/hard levels) covering all 58 cases, with at least one easy and one medium query per case.
- CI via GitHub Actions (`.github/workflows/ci.yml`) that runs the validator on push and pull request.
- A 19-article domain learning knowledge base in `docs/llmstudy/` for LLM onboarding.

## Planned Retrieval Knowledge Base

Future work is intended to use official ruling and rule materials as a source-grounded retrieval corpus:
```text
official Q&A / rule documents -> parsing and chunking -> embeddings and metadata -> retrieval -> ruling judgments
```
Large-scale collection has not been implemented. The project is seeking guidance on appropriate access and permitted use.

## Not Implemented Yet

- An official knowledge base: bulk collection, parsing, chunking, and embedding of KONAMI Q&A / rule documents.
- A retrieval pipeline, knowledge graph, and an evaluation runner (recall@k, MRR) for the eval set.

## Disclaimer

This is an unofficial research project, not affiliated with, endorsed by, or sponsored by KONAMI.
Yu-Gi-Oh! and related official materials belong to their respective rights holders. This repository does not contain or redistribute a bulk copy of KONAMI's official Q&A database or rule documents.

Key files: `docs/schema.md`, `docs/cases_json_template.md`, `gold_cases/operation_legality_cases.jsonl`, `eval/rag_eval_set.jsonl`, and `log/ygo_json_case_changelog.md`.
