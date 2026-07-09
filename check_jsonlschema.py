"""Validate JSONL cases with JSON Schema plus project-level business rules."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
except ModuleNotFoundError:
    print(
        "[ERROR] Missing dependency 'jsonschema'. "
        "Install it with: python -m pip install -r requirements-dev.txt"
    )
    sys.exit(2)


ROOT = Path(__file__).resolve().parent
DEFAULT_SCHEMA = ROOT / "docs" / "operation_case.schema.json"
GOLD_DIR = ROOT / "gold_cases"
GOLD_JSON_DIR = GOLD_DIR / "json"
DEFAULT_JSONL = GOLD_DIR / "operation_legality_cases.jsonl"
APPROVED_LOCAL_SOURCES = {
    # Secondary references providing Simplified Chinese card text from the
    # local cards.cdb when no KONAMI official CN page exists for a card.
    "local_cards_cdb",
}

JSONCase = dict[str, Any]
CaseRule = Callable[[JSONCase, Path], list["ValidationIssue"]]


def json_path(parts: Sequence[object]) -> str:
    """Render jsonschema path parts as a compact JSON path."""
    result = "$"
    for part in parts:
        result += f"[{part}]" if isinstance(part, int) else f".{part}"
    return result


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One validation error with enough context for CLI or programmatic use."""

    file_path: Path
    location: str
    message: str
    line_number: int | None = None

    def render(self) -> str:
        line = f":{self.line_number}" if self.line_number is not None else ""
        return f"[ERROR] {self.file_path}{line} {self.location}: {self.message}"


@dataclass(slots=True)
class ValidationResult:
    """Cases parsed from one JSONL file and all issues found in that file."""

    cases: list[JSONCase] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.issues

    @property
    def error_count(self) -> int:
        return len(self.issues)


class CaseDatasetValidator:
    """Own the schema validator and all dataset-level validation rules."""

    def __init__(
        self,
        schema_path: Path = DEFAULT_SCHEMA,
        main_jsonl: Path = DEFAULT_JSONL,
        gold_dir: Path = GOLD_DIR,
        gold_json_dir: Path | None = None,
    ) -> None:
        self.schema_path = schema_path
        self.main_jsonl = main_jsonl
        self.gold_dir = gold_dir
        self.gold_json_dir = gold_json_dir if gold_json_dir is not None else gold_dir / "json"
        self.schema_validator = self._load_schema_validator()
        self._case_rules: dict[str, CaseRule] = {
            "case_003": self._validate_case_003,
            "case_005": self._validate_case_005,
        }

    def _load_schema_validator(self) -> Draft202012Validator:
        with self.schema_path.open("r", encoding="utf-8") as file:
            schema = json.load(file)
        Draft202012Validator.check_schema(schema)
        return Draft202012Validator(schema, format_checker=FormatChecker())

    @staticmethod
    def _issue(
        file_path: Path,
        location: str,
        message: str,
        line_number: int | None = None,
    ) -> ValidationIssue:
        return ValidationIssue(file_path, location, message, line_number)

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate one JSONL file through schema, business, and mirror layers."""
        result = ValidationResult()
        business_cases: list[JSONCase] = []

        with file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    result.issues.append(
                        self._issue(file_path, "$", "blank lines are not allowed", line_number)
                    )
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError as exc:
                    result.issues.append(
                        self._issue(file_path, "$", f"invalid JSON: {exc}", line_number)
                    )
                    continue

                result.cases.append(data)
                schema_issues = self._validate_case_schema(data, file_path, line_number)
                result.issues.extend(schema_issues)
                if not schema_issues:
                    business_cases.append(data)

        result.issues.extend(self.validate_business_rules(business_cases, file_path))
        result.issues.extend(self.validate_gold_mirrors(result.cases, file_path))
        return result

    def _validate_case_schema(
        self,
        case: JSONCase,
        file_path: Path,
        line_number: int,
    ) -> list[ValidationIssue]:
        errors = sorted(
            self.schema_validator.iter_errors(case),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        return [
            self._issue(
                file_path,
                json_path(error.absolute_path),
                error.message,
                line_number,
            )
            for error in errors
        ]

    def validate_business_rules(
        self,
        cases: list[JSONCase],
        file_path: Path,
    ) -> list[ValidationIssue]:
        """Validate rules involving multiple fields, cases, or files."""
        issues: list[ValidationIssue] = []

        def report(case_id: str, location: str, message: str) -> None:
            issues.append(self._issue(file_path, f"{case_id}.{location}", message))

        ids = [case.get("id") for case in cases]
        if len(ids) != len(set(ids)):
            issues.append(self._issue(file_path, "$", "case ids must be globally unique"))

        expected = [f"case_{index:03d}" for index in range(1, len(cases) + 1)]
        if ids != expected:
            issues.append(
                self._issue(file_path, "$.id", f"case ids must be sequential; got {ids!r}")
            )

        all_source_ids: list[str] = []
        for case in cases:
            case_id = str(case.get("id", "<unknown>"))
            pre_state = case.get("pre_state", {})
            links = pre_state.get("chain_state", {}).get("current_chain_links", [])
            chain_ids = [link.get("chain_id") for link in links if isinstance(link, dict)]
            if len(chain_ids) != len(set(chain_ids)):
                report(
                    case_id,
                    "pre_state.chain_state.current_chain_links",
                    "chain ids must be unique",
                )

            attempted = case.get("attempted_operation", {})
            for key in ("chain_response_to", "chain_id_to_resolve"):
                if key in attempted and attempted[key] not in chain_ids:
                    report(case_id, f"attempted_operation.{key}", "must reference current_chain_links")

            attempted_op_type = attempted.get("operation_type", "")
            case_task_type = case.get("task_type", "")

            if attempted_op_type == "resolve_effect" and case_task_type != "effect_resolution_judgment":
                report(case_id, "task_type",
                       "resolve_effect requires task_type effect_resolution_judgment")

            if case_task_type == "effect_resolution_judgment" and attempted_op_type != "resolve_effect":
                report(case_id, "task_type",
                       "effect_resolution_judgment requires operation_type resolve_effect")

            reasoning_count = len(case.get("gold_answer", {}).get("reasoning_steps", []))
            sources = case.get("gold_answer", {}).get("required_sources", [])
            has_ja_card_text = False
            has_zh_cn_text_cover = False
            has_fake_official_cn = False
            for source_index, source in enumerate(sources):
                if not isinstance(source, dict):
                    continue
                all_source_ids.append(source.get("id"))
                source_type = source.get("source_type")
                language = source.get("language")
                authority = source.get("authority", "")
                source_url = source.get("url", "")
                if source_type == "official_card_text" and language == "ja":
                    has_ja_card_text = True
                if source_type == "official_card_text" and language == "zh-CN":
                    has_zh_cn_text_cover = True
                    if "local-cdb://" in str(source_url):
                        has_fake_official_cn = True
                if source_type == "secondary_reference" and language == "zh-CN" and authority in APPROVED_LOCAL_SOURCES:
                    if str(source_url).startswith("local-cdb://"):
                        has_zh_cn_text_cover = True
                    else:
                        report(
                            case_id,
                            f"gold_answer.required_sources[{source_index}].url",
                            "local secondary reference must use local-cdb:// URI",
                        )
                if source_type == "official_ruling" and not source.get("source_updated_at"):
                    report(
                        case_id,
                        f"gold_answer.required_sources[{source_index}].source_updated_at",
                        "official_ruling sources must include source_updated_at",
                    )
                for step in source.get("supports_reasoning_steps", []):
                    if isinstance(step, int) and step > reasoning_count:
                        report(
                            case_id,
                            (
                                "gold_answer.required_sources"
                                f"[{source_index}].supports_reasoning_steps"
                            ),
                            f"step {step} exceeds reasoning_steps length {reasoning_count}",
                        )

            if not has_ja_card_text:
                report(
                    case_id,
                    "gold_answer.required_sources",
                    "formal cases must include at least one ja official_card_text source",
                )
            if not has_zh_cn_text_cover:
                report(
                    case_id,
                    "gold_answer.required_sources",
                    "formal cases must include zh-CN official_card_text or approved local secondary reference",
                )
            if has_fake_official_cn:
                report(
                    case_id,
                    "gold_answer.required_sources",
                    "local-cdb:// URI must use secondary_reference, not official_card_text",
                )

            issues.extend(self._validate_column_mapping(case, file_path))
            issues.extend(self._validate_resolution_history(case, file_path))

            case_rule = self._case_rules.get(case_id)
            if case_rule is not None:
                issues.extend(case_rule(case, file_path))

        if len(all_source_ids) != len(set(all_source_ids)):
            issues.append(
                self._issue(
                    file_path,
                    "$.gold_answer.required_sources",
                    "source ids must be globally unique",
                )
            )
        return issues

    def _validate_resolution_history(
        self,
        case: JSONCase,
        file_path: Path,
    ) -> list[ValidationIssue]:
        """Validate resolved chain history against the current timing context."""
        issues: list[ValidationIssue] = []
        case_id = str(case.get("id", "<unknown>"))
        pre_state = case.get("pre_state", {})
        chain_state = pre_state.get("chain_state", {})
        links = chain_state.get("current_chain_links", [])
        chain_ids = [link.get("chain_id") for link in links if isinstance(link, dict)]
        chain_numbers = {
            chain_id: int(str(chain_id)[1:])
            for chain_id in chain_ids
            if isinstance(chain_id, str) and re.fullmatch(r"C[1-9][0-9]*", chain_id)
        }
        history = pre_state.get("resolution_history", [])

        def issue(location: str, message: str) -> None:
            issues.append(self._issue(file_path, f"{case_id}.{location}", message))

        if not isinstance(history, list):
            return issues

        resolved_ids: list[str] = []
        resolved_numbers: list[int] = []
        for index, item in enumerate(history):
            if not isinstance(item, dict):
                continue
            resolved_id = item.get("resolved_chain_id")
            if isinstance(resolved_id, str):
                resolved_ids.append(resolved_id)
                if chain_ids and resolved_id not in chain_ids:
                    issue(
                        f"pre_state.resolution_history[{index}].resolved_chain_id",
                        "must reference current_chain_links when current chain context is present",
                    )
                if re.fullmatch(r"C[1-9][0-9]*", resolved_id):
                    resolved_numbers.append(int(resolved_id[1:]))
            if item.get("result") == []:
                issue(
                    f"pre_state.resolution_history[{index}].result",
                    "resolved chain history cannot contain an empty result",
                )

        if len(resolved_ids) != len(set(resolved_ids)):
            issue("pre_state.resolution_history", "resolved_chain_id values must be unique")

        if resolved_numbers != sorted(resolved_numbers, reverse=True):
            issue(
                "pre_state.resolution_history",
                "resolved chain history must follow actual chain resolution order from higher chain id to lower chain id",
            )

        if chain_state.get("is_chain_building") and history:
            issue(
                "pre_state.resolution_history",
                "chain-building states cannot already have resolved chain history",
            )

        state_timing = str(pre_state.get("state_timing") or "")
        required_after_ids = {
            f"C{match}"
            for match in re.findall(r"after_C([1-9][0-9]*)_resolved", state_timing)
        }
        for required_id in required_after_ids:
            if required_id not in resolved_ids:
                issue(
                    "pre_state.resolution_history",
                    f"state_timing says {required_id} resolved, but it is missing from history",
                )

        pending_ids = {
            f"C{match}"
            for match in re.findall(r"before_resolving_C([1-9][0-9]*)", state_timing)
        }
        attempted = case.get("attempted_operation", {})
        if isinstance(attempted.get("chain_id_to_resolve"), str):
            pending_ids.add(attempted["chain_id_to_resolve"])

        for pending_id in pending_ids:
            if not re.fullmatch(r"C[1-9][0-9]*", pending_id):
                continue
            pending_number = int(pending_id[1:])
            invalid = [rid for rid in resolved_ids if re.fullmatch(r"C[1-9][0-9]*", rid) and int(rid[1:]) <= pending_number]
            if invalid:
                issue(
                    "pre_state.resolution_history",
                    f"history contains {invalid!r}, but {pending_id} and lower chain links have not resolved yet",
                )

        return issues

    def _validate_column_mapping(
        self,
        case: JSONCase,
        file_path: Path,
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        case_id = str(case.get("id", "<unknown>"))
        pre_state = case.get("pre_state", {})

        for side, expected_columns in (
            ("self_state", [1, 2, 3, 4, 5]),
            ("opponent_state", [5, 4, 3, 2, 1]),
        ):
            field_state = pre_state.get(side, {}).get("field", {})
            for group, prefix in (("monster_zones", "m"), ("spell_trap_zones", "s")):
                zones = field_state.get(group, {})
                actual = [
                    zones.get(f"{prefix}{index}", {}).get("column_index")
                    for index in range(1, 6)
                ]
                if actual != expected_columns:
                    issues.append(
                        self._issue(
                            file_path,
                            f"{case_id}.pre_state.{side}.field.{group}",
                            f"invalid column mapping {actual!r}",
                        )
                    )
        return issues

    def _validate_case_003(
        self,
        case: JSONCase,
        file_path: Path,
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        constraints = case.get("pre_state", {}).get("known_constraints", [])
        attacks = [
            constraint
            for constraint in constraints
            if isinstance(constraint, dict) and constraint.get("type") == "attack_restriction"
        ]
        if len(attacks) != 1 or attacks[0].get("effect_scope") != "monster":
            issues.append(
                self._issue(
                    file_path,
                    "case_003.pre_state.known_constraints",
                    "legal case_003 requires a monster-scoped attack restriction",
                )
            )
        if case.get("gold_answer", {}).get("label") != "legal":
            issues.append(
                self._issue(
                    file_path,
                    "case_003.gold_answer.label",
                    "case_003 must remain legal",
                )
            )
        return issues

    def _validate_case_005(
        self,
        case: JSONCase,
        file_path: Path,
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        links = (
            case.get("pre_state", {})
            .get("chain_state", {})
            .get("current_chain_links", [])
        )
        features = set(links[0].get("effect_features", [])) if links else set()
        required = {
            "perform_link_summon_after_chain_link_resolution",
            "includes_special_summon_effect",
            "resulting_monster_not_summoned_by_activated_effect",
        }
        if not required <= features:
            issues.append(
                self._issue(
                    file_path,
                    "case_005.pre_state.chain_state.current_chain_links[0].effect_features",
                    "missing I:P three-part semantics",
                )
            )

        answer = case.get("gold_answer", {})
        if answer.get("label") != "illegal" or answer.get("failed_check") != "activation_condition":
            issues.append(
                self._issue(
                    file_path,
                    "case_005.gold_answer",
                    "case_005 must remain illegal / activation_condition",
                )
            )
        return issues

    def validate_gold_mirrors(
        self,
        cases: list[JSONCase],
        jsonl_path: Path,
    ) -> list[ValidationIssue]:
        """Require formatted gold JSON files to exactly mirror the main JSONL."""
        if jsonl_path.resolve() != self.main_jsonl.resolve():
            return []

        issues: list[ValidationIssue] = []
        gold_paths = sorted(self.gold_json_dir.glob("case*.json"))
        if len(gold_paths) != len(cases):
            issues.append(
                self._issue(
                    self.gold_json_dir,
                    "$",
                    f"expected {len(cases)} gold files, found {len(gold_paths)}",
                )
            )

        main_by_id = {case.get("id"): case for case in cases}
        for gold_path in gold_paths:
            try:
                gold = json.loads(gold_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                issues.append(self._issue(gold_path, "$", str(exc)))
                continue
            if main_by_id.get(gold.get("id")) != gold:
                issues.append(self._issue(gold_path, "$", "object differs from main JSONL"))
        return issues

    def run_self_tests(self, cases: list[JSONCase]) -> list[str]:
        """Run deterministic negative scenarios against schema and business rules."""
        failures: list[str] = []

        def schema_must_fail(name: str, case: JSONCase) -> None:
            if not list(self.schema_validator.iter_errors(case)):
                failures.append(f"{name}: schema unexpectedly accepted invalid case")

        def business_must_fail(name: str, case: JSONCase) -> None:
            if not self.validate_business_rules([case], Path("<self-test>")):
                failures.append(f"{name}: business rules unexpectedly accepted invalid case")

        by_id = {case["id"]: case for case in cases}

        bad = copy.deepcopy(by_id["case_001"])
        bad["gold_answer"]["label"] = "legalx"
        schema_must_fail("invalid label", bad)

        bad = copy.deepcopy(by_id["case_001"])
        bad["gold_answer"]["label"] = "depends"
        bad["gold_answer"]["missing_info"] = []
        schema_must_fail("empty depends missing_info", bad)

        bad = copy.deepcopy(by_id["case_005"])
        bad["pre_state"]["chain_state"]["current_chain_links"][0]["effect_features"] = [
            "grant_link_summon_opportunity"
        ]
        schema_must_fail("deprecated feature", bad)

        bad = copy.deepcopy(by_id["case_001"])
        del bad["gold_answer"]["required_sources"][0]["url"]
        schema_must_fail("missing source URL", bad)

        bad = copy.deepcopy(by_id["case_001"])
        bad["attempted_operation"]["declared_cost"][0]["type"] = "throw_away"
        schema_must_fail("invalid cost", bad)

        bad = copy.deepcopy(by_id["case_001"])
        bad["attempted_operation"]["chain_response_to"] = "C99"
        business_must_fail("broken chain reference", bad)

        bad = copy.deepcopy(by_id["case_001"])
        del bad["pre_state"]["resolution_history"]
        schema_must_fail("missing resolution_history", bad)

        bad = copy.deepcopy(by_id["case_025"])
        bad["pre_state"]["resolution_history"][0]["resolved_chain_id"] = "C99"
        business_must_fail("broken resolution_history reference", bad)

        bad = copy.deepcopy(by_id["case_002"])
        bad["pre_state"]["resolution_history"] = list(reversed(bad["pre_state"]["resolution_history"]))
        business_must_fail("wrong resolution_history order", bad)

        bad = copy.deepcopy(by_id["case_025"])
        bad["pre_state"]["resolution_history"][0]["result"] = []
        schema_must_fail("empty resolution_history result", bad)

        bad = copy.deepcopy(by_id["case_002"])
        bad["attempted_operation"]["operation_type"] = "activate_effect"
        business_must_fail("effect_resolution_judgment with non-resolve operation", bad)

        bad = copy.deepcopy(by_id["case_001"])
        bad["gold_answer"]["required_sources"] = [
            source
            for source in bad["gold_answer"]["required_sources"]
            if not (
                source.get("source_type") == "official_card_text"
                and source.get("language") == "zh-CN"
            )
        ]
        business_must_fail("missing zh-CN official card text", bad)

        bad = copy.deepcopy(by_id["case_041"])
        for source in bad["gold_answer"]["required_sources"]:
            if source.get("source_type") == "official_ruling":
                source.pop("source_updated_at", None)
        business_must_fail("official ruling missing source_updated_at", bad)

        bad = copy.deepcopy(by_id["case_001"])
        bad["gold_answer"]["required_sources"] = [
            source
            for source in bad["gold_answer"]["required_sources"]
            if not (
                source.get("source_type") == "official_card_text"
                and source.get("language") == "zh-CN"
            )
        ]
        business_must_fail("missing zh-CN text cover", bad)

        bad = copy.deepcopy(by_id["case_041"])
        bad["gold_answer"]["required_sources"].append({
            "id": "src_case_041_06",
            "source_type": "official_card_text",
            "authority": "KONAMI",
            "title": "local card text",
            "url": "local-cdb://cards.cdb/texts/99999999",
            "official_id": "cid:99999999",
            "language": "zh-CN",
            "accessed_at": "2026-07-08",
            "supports_reasoning_steps": [1]
        })
        business_must_fail("local-cdb disguised as official_card_text", bad)

        bad = copy.deepcopy(by_id["case_041"])
        bad["gold_answer"]["required_sources"].append({
            "id": "src_case_041_07",
            "source_type": "secondary_reference",
            "authority": "local_cards_cdb",
            "title": "local card text",
            "url": "https://example.com/card.txt",
            "language": "zh-CN",
            "accessed_at": "2026-07-08",
            "supports_reasoning_steps": [1]
        })
        business_must_fail("local secondary missing local-cdb:// URI", bad)
        return failures

    @staticmethod
    def self_test_count() -> int:
        """Number of deterministic negative scenarios in run_self_tests."""
        return 16


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Yu-Gi-Oh! JSONL cases with JSON Schema and project rules."
    )
    parser.add_argument(
        "--schemafile",
        "-s",
        type=Path,
        default=DEFAULT_SCHEMA,
        help=f"JSON Schema file (default: {DEFAULT_SCHEMA})",
    )
    parser.add_argument(
        "jsonl_files",
        nargs="*",
        type=Path,
        default=[DEFAULT_JSONL],
        help=f"JSONL files (default: {DEFAULT_JSONL})",
    )
    parser.add_argument("--self-test", action="store_true", help="run in-memory negative tests")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        validator = CaseDatasetValidator(schema_path=args.schemafile)
    except FileNotFoundError:
        print(f"[ERROR] Schema file not found: {args.schemafile}")
        return 2
    except json.JSONDecodeError as exc:
        print(f"[ERROR] Invalid schema JSON: {exc}")
        return 2
    except SchemaError as exc:
        print(f"[ERROR] Invalid JSON Schema at {json_path(exc.absolute_schema_path)}: {exc.message}")
        return 2

    total_errors = 0
    first_cases: list[JSONCase] | None = None
    for file_path in args.jsonl_files:
        if not file_path.is_file():
            print(f"[ERROR] File not found: {file_path}")
            total_errors += 1
            continue

        print(f"Validating {file_path}...")
        result = validator.validate_file(file_path)
        if first_cases is None:
            first_cases = result.cases

        for issue in result.issues:
            print(issue.render())

        if result.is_valid:
            print(f"[OK] {file_path} passed schema and business validation.")
        else:
            print(f"[FAIL] {file_path} had {result.error_count} error(s).")
        total_errors += result.error_count

    if args.self_test and first_cases:
        failures = validator.run_self_tests(first_cases)
        if failures:
            for failure in failures:
                print(f"[SELF-TEST ERROR] {failure}")
            total_errors += len(failures)
        else:
            print(f"[OK] {validator.self_test_count()} negative validation scenarios rejected.")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
