# Yu-Gi-Oh! Operation Legality Judgment Dataset

This project defines a structured dataset for evaluating Yu-Gi-Oh! ruling legality.
Given a known game state and a proposed operation, it determines whether the operation
or a declared effect resolution is legal under the relevant rules.

The scope is ruling correctness only: it does not recommend plays, build decks,
simulate complete duels, or perform strategic analysis.

## Implemented

- A JSONL case format for operation-legality judgments.
- A documented schema for game state, chains, zones, columns, and gold answers.
- Fixed v1 enums for `operation_type` and `effect_features`.
- Fixed `C1` / `C2` / `C3` chain identifiers and `column_index` mapping rules.
- Templates for activation/chaining and effect-resolution cases.
- Two manually curated gold cases: Ash Blossom chaining and Infinite Impermanence column negation.

## Not Implemented Yet

- A validated collection of 10 seed cases and 50 human-verified gold cases.
- A machine-readable JSON Schema and automatic dataset validation.
- An official ruling knowledge base with source IDs and provenance.
- Vector, BM25, hybrid retrieval, or a knowledge graph.
- A RAG inference pipeline, Ragas conversion layer, and domain-specific evaluation metrics.

Key files: `schema.md`, `cases_json模板.md`, `gpt_to_codex/operation_legality_cases.jsonl`, and `ygo_json_case_changelog.md`.
