from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


CATEGORIES = {"hard_requirement", "core_capability", "bonus_signal"}
PRIORITIES = {"high", "medium", "low"}
STATUSES = {"strong_match", "partial_match", "transferable", "unmatched"}
HASH = re.compile(r"^[0-9a-fA-F]{64}$")


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _strings(value: object) -> bool:
    return isinstance(value, list) and all(_text(item) for item in value)


def validate(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["JD match report must be an object"]
    required = {
        "schema_version", "jd_source", "target_role", "organization",
        "requirements", "matches", "unmatched_requirement_ids",
        "clarification_candidates", "role_specific_copy_layer_id",
    }
    errors = [f"missing field: {key}" for key in sorted(required - set(payload))]
    if errors:
        return errors
    if payload["schema_version"] != 1:
        errors.append("schema_version must be 1")
    source = payload["jd_source"]
    if not isinstance(source, dict) or not all(
        _text(source.get(key)) for key in ("source_id", "path", "sha256")
    ):
        errors.append("jd_source must include source_id, path, and sha256")
    elif not HASH.fullmatch(source["sha256"]):
        errors.append("jd_source.sha256 must be SHA-256")
    for key in ("target_role", "organization"):
        if not isinstance(payload[key], str):
            errors.append(f"{key} must be a string")

    requirements = payload["requirements"]
    requirement_ids: list[str] = []
    if not isinstance(requirements, list) or not requirements:
        errors.append("requirements must be a non-empty list")
        requirements = []
    for index, item in enumerate(requirements):
        if not isinstance(item, dict):
            errors.append(f"requirement[{index}] must be an object")
            continue
        item_id = item.get("id")
        label = item_id if _text(item_id) else f"requirement[{index}]"
        if not all(_text(item.get(key)) for key in ("id", "exact_phrase", "normalized_concept")):
            errors.append(f"{label} requires id, exact_phrase, and normalized_concept")
        else:
            requirement_ids.append(item_id)
        if item.get("category") not in CATEGORIES:
            errors.append(f"{label} has invalid category")
        if item.get("priority") not in PRIORITIES:
            errors.append(f"{label} has invalid priority")
    if len(requirement_ids) != len(set(requirement_ids)):
        errors.append("requirement IDs must be unique")

    matches = payload["matches"]
    matched_ids: list[str] = []
    unmatched: set[str] = set()
    if not isinstance(matches, list):
        errors.append("matches must be a list")
        matches = []
    for index, row in enumerate(matches):
        if not isinstance(row, dict):
            errors.append(f"match[{index}] must be an object")
            continue
        item_id = row.get("jd_item_id")
        label = item_id if _text(item_id) else f"match[{index}]"
        if item_id not in requirement_ids:
            errors.append(f"{label} references an unknown requirement")
        else:
            matched_ids.append(item_id)
        status = row.get("status")
        if status not in STATUSES:
            errors.append(f"{label} has invalid match status")
        facts = row.get("fact_ids")
        evidence = row.get("evidence_ids")
        if not _strings(facts) or not _strings(evidence):
            errors.append(f"{label} fact_ids and evidence_ids must be string lists")
            facts, evidence = [], []
        if not _text(row.get("resume_location")) or not _text(row.get("rationale")):
            errors.append(f"{label} requires resume_location and rationale")
        if status == "unmatched":
            unmatched.add(str(item_id))
            if facts or evidence:
                errors.append(f"{label} unmatched rows cannot cite facts or evidence")
        elif status in STATUSES and (not facts or not evidence):
            errors.append(f"{label} matched rows require fact_ids and evidence_ids")
    if set(matched_ids) != set(requirement_ids) or len(matched_ids) != len(requirement_ids):
        errors.append("matches must contain exactly one row per requirement")
    unmatched_ids = payload["unmatched_requirement_ids"]
    if not _strings(unmatched_ids) or set(unmatched_ids) != unmatched:
        errors.append("unmatched_requirement_ids must equal unmatched match rows")
    if not _strings(payload["clarification_candidates"]):
        errors.append("clarification_candidates must be a string list")
    layer = payload["role_specific_copy_layer_id"]
    if layer is not None and not _text(layer):
        errors.append("role_specific_copy_layer_id must be null or a non-empty string")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an evidence-linked JD match report")
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"ERROR: could not read JD match report: {error}")
        return 1
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: JD match report is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
