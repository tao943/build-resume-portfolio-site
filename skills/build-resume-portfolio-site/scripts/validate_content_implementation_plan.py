from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED = {"schema_version", "design_spec_id", "tasks", "handoff_criteria"}
TASK_FIELDS = {
    "id",
    "fact_ids",
    "evidence_ids",
    "target_files",
    "produces",
    "blocked_claims",
    "verification",
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
        return ["content implementation plan must be a JSON object"]
    errors = [
        f"missing field: {name}"
        for name in sorted(REQUIRED - set(payload))
    ]
    if errors:
        return errors
    if payload["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if not isinstance(payload["design_spec_id"], str) or not payload[
        "design_spec_id"
    ].strip():
        errors.append("design_spec_id must be a non-empty string")
    if not _strings(payload["handoff_criteria"], non_empty=True):
        errors.append("handoff_criteria must be non-empty")

    tasks = payload["tasks"]
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty list")
        return errors
    ids: list[str] = []
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"task[{index}] must be an object")
            continue
        missing = TASK_FIELDS - set(task)
        if missing:
            errors.append(
                f"task[{index}] missing fields: {', '.join(sorted(missing))}"
            )
            continue
        task_id = task["id"]
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append(f"task[{index}].id must be non-empty")
        else:
            ids.append(task_id)
        for field in ("fact_ids", "evidence_ids", "blocked_claims"):
            if not _strings(task[field]):
                errors.append(f"{task_id}.{field} must be a string list")
        for field in ("target_files", "produces", "verification"):
            if not _strings(task[field], non_empty=True):
                errors.append(f"{task_id}.{field} must be non-empty")
        if not task["fact_ids"] and not task["evidence_ids"] and not task[
            "blocked_claims"
        ]:
            errors.append(
                f"{task_id} requires facts, evidence, or an explicit block"
            )
    if len(ids) != len(set(ids)):
        errors.append("task IDs must be unique")
    if _contains_placeholder(payload):
        errors.append("placeholder text is not allowed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a content implementation plan."
    )
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read content implementation plan: {exc}")
        return 1
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: content implementation plan is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
