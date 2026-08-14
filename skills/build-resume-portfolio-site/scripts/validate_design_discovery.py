from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


EXPECTED_DOMAINS = {
    "structure": ["landing", "style", "product", "ux"],
    "typography": ["typography", "style", "ux"],
    "color": ["color", "style", "ux"],
    "media": ["style", "product", "landing", "ux"],
    "primary_motion": ["motion", "style", "landing", "ux"],
    "secondary_motion": ["motion", "react", "ux"],
}
PRIVACY_SENSITIVE_KEYS = {
    "full_name",
    "email",
    "phone",
    "telephone",
    "address",
    "location",
    "wechat",
    "weixin",
    "qq",
    "contact",
    "contact_details",
    "raw_resume",
    "resume_text",
    "project_secret",
}
BASELINE_DIRECTION_FIELDS = {
    "id",
    "name",
    "style_family",
    "composition",
    "color_relationships",
    "typography_roles",
    "surface_language",
    "media_strategy",
    "fit_reasons",
    "risks",
    "source_ids",
}
CANDIDATE_LIST_FIELDS = (
    "fit",
    "risks",
    "tradeoffs",
    "accessibility_notes",
    "source_ids",
)


def _string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _strings(value: Any, *, non_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not non_empty)
        and all(_string(item) for item in value)
    )


def _privacy_errors(
    value: Any, forbidden_keys: set[str] = PRIVACY_SENSITIVE_KEYS
) -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).strip().casefold() in forbidden_keys:
                errors.append(f"privacy-sensitive key is not allowed: {key}")
            errors.extend(_privacy_errors(child, forbidden_keys))
    elif isinstance(value, list):
        for child in value:
            errors.extend(_privacy_errors(child, forbidden_keys))
    return errors


def _validate_provenance(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["provenance must be an object"]
    errors: list[str] = []
    for field in ("upstream", "catalog_version"):
        if not _string(value.get(field)):
            errors.append(f"provenance requires {field}")
    return errors


def _validate_baseline(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("mode") != "baseline":
        errors.append("baseline mode must be baseline")
    directions = payload.get("candidate_directions")
    if not isinstance(directions, list) or len(directions) != 3:
        errors.append("baseline requires exactly three directions")
        directions = []
    ids: list[str] = []
    for index, direction in enumerate(directions):
        if not isinstance(direction, dict):
            errors.append(f"direction[{index}] must be an object")
            continue
        missing = BASELINE_DIRECTION_FIELDS - set(direction)
        if missing:
            errors.append(
                f"direction[{index}] missing fields: {', '.join(sorted(missing))}"
            )
        direction_id = direction.get("id")
        if _string(direction_id):
            ids.append(direction_id)
        else:
            errors.append(f"direction[{index}] requires an ID")
        if not _strings(direction.get("source_ids"), non_empty=True):
            errors.append(f"direction {direction_id or index} requires source_ids")
    if len(ids) != len(set(ids)):
        errors.append("direction IDs must be unique")
    if payload.get("selected_direction_id") not in ids:
        errors.append("selected direction must reference a candidate")
    errors.extend(_validate_provenance(payload.get("provenance")))
    return errors


def _validate_category(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    category = payload.get("category")
    if category not in EXPECTED_DOMAINS:
        return ["unsupported design category"]
    if payload.get("domains_searched") != EXPECTED_DOMAINS[category]:
        errors.append(f"{category} domains do not match contract")

    inherited = payload.get("inherited_decision_ids")
    context = payload.get("query_context")
    if not isinstance(context, dict) or inherited != context.get(
        "approved_decision_ids"
    ):
        errors.append("inherited decisions do not match query context")
    if not _strings(inherited):
        errors.append("inherited_decision_ids must be a string list")

    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or len(candidates) < 2:
        errors.append("category requires at least two candidates")
        candidates = []
    ids: list[str] = []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append("candidate must be an object")
            continue
        candidate_id = candidate.get("id")
        if not _string(candidate_id):
            errors.append(f"candidate[{index}] requires an ID")
            candidate_id = str(index)
        else:
            ids.append(candidate_id)
        if not _string(candidate.get("label")):
            errors.append(f"candidate {candidate_id} requires a label")
        for field in CANDIDATE_LIST_FIELDS:
            if not _strings(candidate.get(field), non_empty=True):
                if field == "source_ids":
                    errors.append(f"candidate {candidate_id} requires source_ids")
                else:
                    errors.append(f"candidate {candidate_id} requires {field}")
        if not _strings(candidate.get("compatibility")):
            errors.append(f"candidate {candidate_id} compatibility must be a string list")
        if not _string(candidate.get("responsive_fallback")):
            errors.append(f"candidate {candidate_id} requires responsive_fallback")
    if len(ids) != len(set(ids)):
        errors.append("candidate IDs must be unique")
    if payload.get("recommended_candidate_id") not in ids:
        errors.append("recommendation must reference a candidate")
    errors.extend(_validate_provenance(payload.get("provenance")))
    return errors


def validate(payload: Any, expected_type: str | None = None) -> list[str]:
    if not isinstance(payload, dict):
        return ["design discovery report must be an object"]
    errors: list[str] = []
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    report_type = payload.get("report_type")
    if expected_type is not None and report_type != expected_type:
        errors.append(f"expected report type: {expected_type}")
    errors.extend(_privacy_errors(payload))
    query_payload = payload.get("query")
    if query_payload is None:
        query_payload = payload.get("query_context")
    errors.extend(_privacy_errors(query_payload, {"name"}))
    if report_type == "baseline":
        errors.extend(_validate_baseline(payload))
    elif report_type == "category":
        errors.extend(_validate_category(payload))
    else:
        errors.append("report_type must be baseline or category")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a database-first design discovery report."
    )
    parser.add_argument("report", type=Path)
    parser.add_argument("--expected-type", choices=("baseline", "category"))
    args = parser.parse_args()
    try:
        payload = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"ERROR: could not read design discovery report: {error}")
        return 1
    errors = validate(payload, expected_type=args.expected_type)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: design discovery report is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
