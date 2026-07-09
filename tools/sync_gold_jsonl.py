"""Rebuild the canonical gold JSONL from formatted gold case JSON files."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOLD_DIR = ROOT / "gold_cases"
GOLD_JSON_DIR = GOLD_DIR / "json"
JSONL_PATH = GOLD_DIR / "operation_legality_cases.jsonl"


def main() -> None:
    cases = []
    for case_path in sorted(GOLD_JSON_DIR.glob("case*.json")):
        cases.append(json.loads(case_path.read_text(encoding="utf-8")))

    content = "\n".join(
        json.dumps(case, ensure_ascii=False, separators=(",", ":")) for case in cases
    )
    JSONL_PATH.write_text(content + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
