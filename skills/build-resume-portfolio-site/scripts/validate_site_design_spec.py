from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED = {
    "schema_version",
    "spec_id",
    "workflow_mode",
    "content_revision",
    "visual_protagonist",
    "fixed_constraints",
    "open_ceiling",
    "avoid",
    "alternatives",
    "selected_alternative_id",
    "composition_commitment",
    "type_color_character",
    "representative_interaction",
    "approval",
}
PLACEHOLDERS = {"todo", "tbd", "implement later", "fill in details"}


def _strings(value: Any, *, non_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not non_empty)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def _contains_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in PLACEHOLDERS
    if isinstance(value, list):
        return any(_contains_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_placeholder(item) for item in value.values())
    return False


def validate(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["site design spec must be a JSON object"]
    errors = [
        f"missing field: {name}"
        for name in sorted(REQUIRED - set(payload))
    ]
    if errors:
        return errors
    if payload["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if payload["workflow_mode"] not in {"full", "fast-change"}:
        errors.append("workflow_mode must be full or fast-change")
    if not isinstance(payload["content_revision"], int) or payload[
        "content_revision"
    ] < 1:
        errors.append("content_revision must be a positive integer")
    for name in (
        "spec_id",
        "visual_protagonist",
        "composition_commitment",
        "type_color_character",
        "representative_interaction",
    ):
        if not isinstance(payload[name], str) or not payload[name].strip():
            errors.append(f"{name} must be a non-empty string")
    for name in ("fixed_constraints", "open_ceiling", "avoid"):
        if not _strings(payload[name], non_empty=True):
            errors.append(f"{name} must be a non-empty string list")
    fixed = set(payload["fixed_constraints"])
    avoid = set(payload["avoid"])
    if fixed & avoid:
        errors.append("fixed_constraints and avoid must not overlap")

    alternatives = payload["alternatives"]
    if not isinstance(alternatives, list):
        errors.append("alternatives must be a list")
        alternatives = []
    if payload["workflow_mode"] == "full" and not 2 <= len(alternatives) <= 3:
        errors.append("full mode requires two or three alternatives")
    ids: list[str] = []
    families: list[str] = []
    for index, alternative in enumerate(alternatives):
        if not isinstance(alternative, dict):
            errors.append(f"alternative[{index}] must be an object")
            continue
        if not {"id", "family", "tradeoffs"} <= set(alternative):
            errors.append(f"alternative[{index}] is incomplete")
            continue
        if not all(
            isinstance(alternative[name], str) and alternative[name].strip()
            for name in ("id", "family")
        ):
            errors.append(f"alternative[{index}] id and family are required")
        if not _strings(alternative["tradeoffs"], non_empty=True):
            errors.append(f"alternative[{index}] requires tradeoffs")
        ids.append(alternative["id"])
        families.append(alternative["family"].strip().lower())
    if len(ids) != len(set(ids)):
        errors.append("alternative IDs must be unique")
    if len(families) != len(set(families)):
        errors.append("layout families must be materially different")
    if payload["selected_alternative_id"] not in ids:
        errors.append("selected_alternative_id must reference an alternative")

    approval = payload["approval"]
    if not isinstance(approval, dict):
        errors.append("approval must be an object")
    else:
        if approval.get("status") != "user_approved":
            errors.append("site design requires user approval")
        if approval.get("source") != "explicit_user":
            errors.append("approval source must be explicit_user")
    if _contains_placeholder(payload):
        errors.append("placeholder text is not allowed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a website discovery design specification."
    )
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.spec.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read site design spec: {exc}")
        return 1
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: site design spec is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
