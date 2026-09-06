from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from validate_design_contract import validate as validate_design_contract


ROOT_FIELDS = {
    "schema_version",
    "candidate_id",
    "design_contract",
    "repair_round",
    "captures",
    "deterministic_checks",
    "dimension_reviews",
    "findings",
    "interaction_states_checked",
    "overall_status",
}
STRUCTURE_REVIEW_FIELDS = {"seed_identity", "visual_protagonist", "mobile_transformation", "static_without_motion", "novelty_not_palette_only", "evidence_refs", "contract_paths"}
CAPTURE_FIELDS = {"id", "viewport", "state", "path"}
CHECK_FIELDS = {"rule_id", "status", "evidence_refs", "contract_path", "note"}
REVIEW_FIELDS = {"status", "verdict", "strengths", "evidence_refs", "contract_paths"}
FINDING_FIELDS = {
    "id",
    "rule_id",
    "dimension",
    "severity",
    "viewport_or_state",
    "region",
    "evidence_refs",
    "contract_path",
    "permitted_files",
    "proposed_local_change",
    "intended_result",
}
INTERACTION_FIELDS = {
    "controller_family",
    "target",
    "trigger",
    "capture_refs",
    "coarse_pointer",
    "reduced_motion",
    "status",
}
STATUSES = {"pass", "repairable", "blocking"}
SEVERITIES = {"advisory", "repairable", "blocking"}
FINDING_DIMENSIONS = {
    "identity_fit",
    "aesthetic_quality",
    "accessibility",
    "responsive",
    "runtime_safety",
}
REQUIRED_VIEWPORTS = {"desktop", "tablet", "mobile"}
STATUS_RANK = {"pass": 0, "repairable": 1, "blocking": 2}
SEVERITY_RANK = {"advisory": 0, "repairable": 1, "blocking": 2}


def _string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(_string(item) for item in value)
        and len({item.strip().casefold() for item in value}) == len(value)
    )


def _known_rules(contract: dict[str, Any]) -> set[str]:
    rules = {
        item["rule_id"]
        for item in contract.get("anti_template_rules", [])
        if isinstance(item, dict) and _string(item.get("rule_id"))
    }
    for values in contract.get("acceptance_checks", {}).values():
        if isinstance(values, list):
            rules.update(
                item["rule_id"]
                for item in values
                if isinstance(item, dict) and _string(item.get("rule_id"))
            )
    return rules


def _contract_path_exists(contract: dict[str, Any], path: Any) -> bool:
    if not _string(path):
        return False
    current: Any = contract
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def _validate_evidence(
    refs: Any, path: str, capture_ids: set[str], errors: list[str]
) -> None:
    if not _string_list(refs):
        errors.append(f"{path} must be a non-empty unique string list")
        return
    for ref in refs:
        if ref not in capture_ids:
            errors.append(f"unknown evidence reference at {path}: {ref}")


def validate(audit: Any, design_contract: Any) -> list[str]:
    contract_errors = validate_design_contract(design_contract)
    if contract_errors:
        return [f"invalid design contract: {error}" for error in contract_errors]
    if not isinstance(audit, dict):
        return ["audit must be a JSON object"]
    errors: list[str] = []
    version = audit.get("schema_version")
    expected_root = ROOT_FIELDS | ({"structure_review"} if version == 2 else set())
    if set(audit) != expected_root:
        missing = expected_root - set(audit)
        extra = set(audit) - expected_root
        if missing:
            errors.append("missing root fields: " + ", ".join(sorted(missing)))
        if extra:
            errors.append("unknown root fields: " + ", ".join(sorted(extra)))
        return errors
    if version not in {1, 2}:
        errors.append("schema_version must be 1 or 2")
    for field in ("candidate_id", "design_contract"):
        if not _string(audit[field]):
            errors.append(f"{field} must be a non-empty string")
    repair_round = audit["repair_round"]
    if isinstance(repair_round, bool) or not isinstance(repair_round, int) or not 0 <= repair_round <= 2:
        errors.append("repair_round must be an integer from 0 through 2")

    captures = audit["captures"]
    capture_ids: set[str] = set()
    viewports: set[str] = set()
    if not isinstance(captures, list) or not captures:
        errors.append("captures must be a non-empty list")
    else:
        for index, item in enumerate(captures):
            path = f"captures[{index}]"
            if not isinstance(item, dict) or set(item) != CAPTURE_FIELDS:
                errors.append(f"{path} must contain exactly: " + ", ".join(sorted(CAPTURE_FIELDS)))
                continue
            if not all(_string(item[field]) for field in CAPTURE_FIELDS):
                errors.append(f"{path} fields must be non-empty strings")
                continue
            if item["id"] in capture_ids:
                errors.append(f"duplicate capture id: {item['id']}")
            capture_ids.add(item["id"])
            viewports.add(item["viewport"])
    for viewport in sorted(REQUIRED_VIEWPORTS - viewports):
        errors.append(f"captures must include {viewport} viewport evidence")

    if version == 2:
        review = audit["structure_review"]
        if not isinstance(review, dict) or set(review) != STRUCTURE_REVIEW_FIELDS:
            errors.append("structure_review must contain exactly the v2 structure evidence fields")
        else:
            for field in STRUCTURE_REVIEW_FIELDS - {"evidence_refs", "contract_paths"}:
                if review.get(field) != "pass":
                    errors.append(f"structure review must pass: {field}")
            _validate_evidence(review.get("evidence_refs"), "structure_review.evidence_refs", capture_ids, errors)
            if not _string_list(review.get("contract_paths")):
                errors.append("structure_review.contract_paths must be non-empty")
            else:
                for contract_path in review["contract_paths"]:
                    if not _contract_path_exists(design_contract, contract_path):
                        errors.append(f"unknown contract_path at structure_review: {contract_path}")

    known_rules = _known_rules(design_contract)
    required_rank = 0
    checks = audit["deterministic_checks"]
    if not isinstance(checks, list):
        errors.append("deterministic_checks must be a list")
    else:
        for index, item in enumerate(checks):
            path = f"deterministic_checks[{index}]"
            if not isinstance(item, dict) or set(item) != CHECK_FIELDS:
                errors.append(f"{path} must contain exactly: " + ", ".join(sorted(CHECK_FIELDS)))
                continue
            if item["rule_id"] not in known_rules:
                errors.append(f"unknown rule_id at {path}: {item['rule_id']}")
            if item["status"] not in STATUSES:
                errors.append(f"{path}.status must be pass, repairable, or blocking")
            else:
                required_rank = max(required_rank, STATUS_RANK[item["status"]])
            _validate_evidence(item["evidence_refs"], f"{path}.evidence_refs", capture_ids, errors)
            if not _contract_path_exists(design_contract, item["contract_path"]):
                errors.append(f"unknown contract_path at {path}: {item['contract_path']}")
            if not _string(item["note"]):
                errors.append(f"{path}.note must be a non-empty string")

    reviews = audit["dimension_reviews"]
    if not isinstance(reviews, dict) or set(reviews) != {"identity_fit", "aesthetic_quality"}:
        errors.append("dimension_reviews must contain exactly identity_fit and aesthetic_quality")
    else:
        for dimension in ("identity_fit", "aesthetic_quality"):
            item = reviews[dimension]
            path = f"dimension_reviews.{dimension}"
            if not isinstance(item, dict) or set(item) != REVIEW_FIELDS:
                errors.append(f"{path} must contain exactly: " + ", ".join(sorted(REVIEW_FIELDS)))
                continue
            if item["status"] not in STATUSES:
                errors.append(f"{path}.status must be pass, repairable, or blocking")
            else:
                required_rank = max(required_rank, STATUS_RANK[item["status"]])
            if not _string(item["verdict"]):
                errors.append(f"{path}.verdict must be a non-empty string")
            if not _string_list(item["strengths"]):
                errors.append(f"{path}.strengths must be a non-empty unique string list")
            _validate_evidence(item["evidence_refs"], f"{path}.evidence_refs", capture_ids, errors)
            if not _string_list(item["contract_paths"]):
                errors.append(f"{path}.contract_paths must be a non-empty unique string list")
            else:
                for contract_path in item["contract_paths"]:
                    if not _contract_path_exists(design_contract, contract_path):
                        errors.append(f"unknown contract_path at {path}: {contract_path}")

    findings = audit["findings"]
    finding_ids: set[str] = set()
    if not isinstance(findings, list):
        errors.append("findings must be a list")
    else:
        for index, item in enumerate(findings):
            path = f"findings[{index}]"
            if not isinstance(item, dict) or set(item) != FINDING_FIELDS:
                missing = FINDING_FIELDS - set(item) if isinstance(item, dict) else FINDING_FIELDS
                errors.append(
                    f"{path} must contain exactly finding fields; missing: "
                    + ", ".join(sorted(missing))
                )
                continue
            for field in (
                "id", "rule_id", "viewport_or_state", "region",
                "proposed_local_change", "intended_result",
            ):
                if not _string(item[field]):
                    errors.append(f"{path}.{field} must be a non-empty string")
            if item["id"] in finding_ids:
                errors.append(f"duplicate finding id: {item['id']}")
            finding_ids.add(item["id"])
            if item["rule_id"] not in known_rules:
                errors.append(f"unknown rule_id at {path}: {item['rule_id']}")
            if item["dimension"] not in FINDING_DIMENSIONS:
                errors.append(f"{path}.dimension is invalid")
            if item["severity"] not in SEVERITIES:
                errors.append(f"{path}.severity must be advisory, repairable, or blocking")
            else:
                required_rank = max(required_rank, SEVERITY_RANK[item["severity"]])
            _validate_evidence(item["evidence_refs"], f"{path}.evidence_refs", capture_ids, errors)
            if not _contract_path_exists(design_contract, item["contract_path"]):
                errors.append(f"unknown contract_path at {path}: {item['contract_path']}")
            if not _string_list(item["permitted_files"]):
                errors.append(f"{path}.permitted_files must be a non-empty unique string list")
            else:
                for filename in item["permitted_files"]:
                    candidate = PurePosixPath(filename.replace("\\", "/"))
                    if candidate.is_absolute() or ".." in candidate.parts:
                        errors.append(f"{path}.permitted_files must stay inside the site")

    interactions = audit["interaction_states_checked"]
    if not isinstance(interactions, list):
        errors.append("interaction_states_checked must be a list")
    else:
        for index, item in enumerate(interactions):
            path = f"interaction_states_checked[{index}]"
            if not isinstance(item, dict) or set(item) != INTERACTION_FIELDS:
                errors.append(f"{path} must contain exactly interaction-state fields")
                continue
            for field in ("controller_family", "target", "trigger", "coarse_pointer", "reduced_motion"):
                if not _string(item[field]):
                    errors.append(f"{path}.{field} must be a non-empty string")
            _validate_evidence(item["capture_refs"], f"{path}.capture_refs", capture_ids, errors)
            if item["status"] not in STATUSES:
                errors.append(f"{path}.status must be pass, repairable, or blocking")
            else:
                required_rank = max(required_rank, STATUS_RANK[item["status"]])

    overall = audit["overall_status"]
    if overall not in STATUSES:
        errors.append("overall_status must be pass, repairable, or blocking")
    elif STATUS_RANK[overall] < required_rank:
        errors.append("overall_status understates findings or dimension results")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a portfolio visual audit.")
    parser.add_argument("audit", type=Path)
    parser.add_argument("--design-contract", required=True, type=Path)
    args = parser.parse_args()
    try:
        audit = json.loads(args.audit.read_text(encoding="utf-8"))
        contract = json.loads(args.design_contract.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        print(f"ERROR: report not found: {exc.filename}")
        return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read report: {exc}")
        return 1
    errors = validate(audit, contract)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: visual-audit report is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
