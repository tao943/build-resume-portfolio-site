from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any


STRATEGIES = {"single-agent", "parallel-wave"}
REQUIRED = {
    "schema_version",
    "design_spec_id",
    "todo_plan",
    "todo_plan_approval",
    "generation_mode",
    "strategy_selection",
    "strategy",
    "multi_agent_authorized",
    "multi_agent_plan",
    "tasks",
    "rollback_baseline",
    "snapshot_target",
}
TASK_FIELDS = {
    "id",
    "depends_on",
    "files",
    "consumes",
    "produces",
    "acceptance",
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
        return ["site implementation plan must be a JSON object"]
    errors = [
        f"missing field: {name}"
        for name in sorted(REQUIRED - set(payload))
    ]
    if errors:
        return errors
    if payload["schema_version"] != 2:
        errors.append("schema_version must be 2")
    todo_plan = str(payload["todo_plan"]).replace("\\", "/")
    if PurePosixPath(todo_plan) != PurePosixPath(
        ".resume-site-work/reports/site-todo-plan.md"
    ):
        errors.append(
            "todo_plan must reference "
            ".resume-site-work/reports/site-todo-plan.md"
        )
    approval = payload["todo_plan_approval"]
    if not isinstance(approval, dict):
        errors.append("todo plan requires user approval")
    elif approval.get("status") != "user_approved":
        errors.append("todo plan requires user approval")
    elif (
        approval.get("source") != "explicit_user"
        or approval.get("channel") != "conversation"
    ):
        errors.append(
            "todo plan approval must be explicit and conversational"
        )
    if payload["generation_mode"] != "one-integrated-site":
        errors.append("generation_mode must be one-integrated-site")
    selection = payload["strategy_selection"]
    if not isinstance(selection, dict):
        errors.append("strategy selection must be recorded")
    else:
        conversational = (
            selection.get("status") == "user_selected"
            and selection.get("source") == "explicit_user"
            and selection.get("channel") == "conversation"
        )
        if not conversational:
            errors.append(
                "strategy selection must be explicit and conversational"
            )
        if selection.get("selected") != payload["strategy"]:
            errors.append("strategy must match the explicit strategy selection")
        if selection.get("recommended") not in STRATEGIES:
            errors.append("recommended strategy is unsupported")
        if not _strings(selection.get("reasons"), non_empty=True):
            errors.append("strategy recommendation reasons must be non-empty")
    if payload["strategy"] not in STRATEGIES:
        errors.append("unsupported strategy")
    if not isinstance(payload["multi_agent_authorized"], bool):
        errors.append("multi_agent_authorized must be boolean")
    for name in ("design_spec_id", "rollback_baseline", "snapshot_target"):
        if not isinstance(payload[name], str) or not payload[name].strip():
            errors.append(f"{name} must be a non-empty string")

    multi_agent = payload["strategy"] == "parallel-wave"
    if multi_agent:
        if payload["multi_agent_authorized"] is not True:
            errors.append("multi-agent strategy requires explicit authorization")
        if not isinstance(payload["multi_agent_plan"], str) or not payload[
            "multi_agent_plan"
        ].strip():
            errors.append("multi-agent strategy requires a validated plan")
    elif payload["multi_agent_plan"] is not None:
        errors.append("single-agent strategy must not reference a multi-agent plan")

    tasks = payload["tasks"]
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty list")
        return errors
    ids: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
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
            continue
        ids.append(task_id)
        by_id[task_id] = task
        if not _strings(task["depends_on"]):
            errors.append(f"{task_id}.depends_on must be a string list")
        for field in (
            "files",
            "consumes",
            "produces",
            "acceptance",
            "verification",
        ):
            if not _strings(task[field], non_empty=True):
                errors.append(f"{task_id}.{field} must be non-empty")
    if len(ids) != len(set(ids)):
        errors.append("task IDs must be unique")
    known = set(ids)
    for task_id, task in by_id.items():
        unknown = set(task["depends_on"]) - known
        if unknown:
            errors.append(
                f"{task_id} has unknown dependencies: {', '.join(sorted(unknown))}"
            )
        if task_id in task["depends_on"]:
            errors.append(f"{task_id} cannot depend on itself")

    if payload["strategy"] == "parallel-wave":
        owners: dict[str, str] = {}
        for task_id, task in by_id.items():
            for file_path in task["files"]:
                if file_path in owners:
                    errors.append(
                        "parallel file overlap: "
                        f"{file_path} is owned by {owners[file_path]} and {task_id}"
                    )
                owners[file_path] = task_id
    if _contains_placeholder(payload):
        errors.append("placeholder text is not allowed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a website implementation plan."
    )
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read site implementation plan: {exc}")
        return 1
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: site implementation plan is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
