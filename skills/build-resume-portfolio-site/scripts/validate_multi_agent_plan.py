from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


STRATEGIES = {"parallel-wave"}
ROLES = {"implementation", "review", "integration", "audit"}
MODES = {"write", "read-only"}
WAVE_MODES = {"sequential", "parallel"}
REQUIRED_ROOT = {
    "schema_version",
    "strategy",
    "integration_owner",
    "shared_files",
    "waves",
    "tasks",
}
REQUIRED_TASK = {
    "id",
    "role",
    "mode",
    "depends_on",
    "allowed_files",
    "acceptance",
    "verification",
}
REQUIRED_WAVE = {"id", "mode", "task_ids"}


def _non_empty_strings(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def validate(plan: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["plan must be a JSON object"]

    missing = REQUIRED_ROOT - set(plan)
    if missing:
        errors.append(f"missing root fields: {', '.join(sorted(missing))}")
        return errors

    if plan["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if plan["strategy"] != "parallel-wave":
        errors.append("strategy must be parallel-wave")
    if plan["integration_owner"] != "main-agent":
        errors.append("integration_owner must be main-agent")

    shared_files = plan["shared_files"]
    if not _string_list(shared_files):
        errors.append("shared_files must be a list of non-empty strings")
        shared_files = []
    elif _duplicates(shared_files):
        errors.append("shared_files must not contain duplicates")
    shared_set = set(shared_files)

    tasks = plan["tasks"]
    waves = plan["waves"]
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty list")
        return errors
    if not isinstance(waves, list) or not waves:
        errors.append("waves must be a non-empty list")
        return errors

    task_by_id: dict[str, dict[str, Any]] = {}
    for index, task in enumerate(tasks):
        label = f"task[{index}]"
        if not isinstance(task, dict):
            errors.append(f"{label} must be an object")
            continue
        missing_task = REQUIRED_TASK - set(task)
        if missing_task:
            errors.append(
                f"{label} missing fields: {', '.join(sorted(missing_task))}"
            )
            continue
        task_id = task["id"]
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if task_id in task_by_id:
            errors.append(f"duplicate task id: {task_id}")
            continue
        task_by_id[task_id] = task
        if task["role"] not in ROLES:
            errors.append(f"{task_id}: unsupported role")
        if task["mode"] not in MODES:
            errors.append(f"{task_id}: unsupported mode")
        if not _string_list(task["depends_on"]):
            errors.append(f"{task_id}: depends_on must be a string list")
        if not _string_list(task["allowed_files"]):
            errors.append(f"{task_id}: allowed_files must be a string list")
        if not _non_empty_strings(task["acceptance"]):
            errors.append(f"{task_id}: acceptance must be non-empty")
        if not _non_empty_strings(task["verification"]):
            errors.append(f"{task_id}: verification must be non-empty")
        if task["role"] in {"review", "audit"} and task["mode"] != "read-only":
            errors.append(f"{task_id}: review and audit tasks must be read-only")
        if task["mode"] == "read-only" and task["allowed_files"]:
            errors.append(f"{task_id}: read-only tasks cannot own writable files")
        if task["role"] != "integration":
            for file_path in task["allowed_files"]:
                if file_path in shared_set:
                    errors.append(
                        f"{task_id}: shared file {file_path} requires integration role"
                    )

    task_ids = set(task_by_id)
    for task_id, task in task_by_id.items():
        dependencies = task.get("depends_on", [])
        if isinstance(dependencies, list):
            unknown = set(dependencies) - task_ids
            if unknown:
                errors.append(
                    f"{task_id}: unknown dependencies: {', '.join(sorted(unknown))}"
                )
            if task_id in dependencies:
                errors.append(f"{task_id}: task cannot depend on itself")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            errors.append(f"dependency cycle detected at {task_id}")
            return
        if task_id in visited or task_id not in task_by_id:
            return
        visiting.add(task_id)
        for dependency in task_by_id[task_id].get("depends_on", []):
            if dependency in task_by_id:
                visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in task_by_id:
        visit(task_id)

    wave_ids: set[str] = set()
    scheduled: list[str] = []
    for index, wave in enumerate(waves):
        label = f"wave[{index}]"
        if not isinstance(wave, dict):
            errors.append(f"{label} must be an object")
            continue
        missing_wave = REQUIRED_WAVE - set(wave)
        if missing_wave:
            errors.append(
                f"{label} missing fields: {', '.join(sorted(missing_wave))}"
            )
            continue
        wave_id = wave["id"]
        if not isinstance(wave_id, str) or not wave_id.strip():
            errors.append(f"{label}.id must be a non-empty string")
        elif wave_id in wave_ids:
            errors.append(f"duplicate wave id: {wave_id}")
        else:
            wave_ids.add(wave_id)
        if wave["mode"] not in WAVE_MODES:
            errors.append(f"{wave_id}: unsupported wave mode")
        if not _non_empty_strings(wave["task_ids"]):
            errors.append(f"{wave_id}: task_ids must be non-empty")
            continue
        if _duplicates(wave["task_ids"]):
            errors.append(f"{wave_id}: task_ids must not contain duplicates")
        unknown = set(wave["task_ids"]) - task_ids
        if unknown:
            errors.append(
                f"{wave_id}: unknown tasks: {', '.join(sorted(unknown))}"
            )
        scheduled.extend(wave["task_ids"])

        if wave["mode"] == "parallel":
            if len(wave["task_ids"]) < 2:
                errors.append(f"{wave_id}: parallel wave needs at least two tasks")
            owners: dict[str, str] = {}
            for task_id in wave["task_ids"]:
                task = task_by_id.get(task_id)
                if not task or task.get("mode") != "write":
                    continue
                for file_path in task.get("allowed_files", []):
                    if file_path in owners:
                        errors.append(
                            "parallel file overlap: "
                            f"{file_path} is owned by {owners[file_path]} and {task_id}"
                        )
                    owners[file_path] = task_id

    if _duplicates(scheduled):
        errors.append(
            "tasks may appear in only one wave: "
            + ", ".join(sorted(_duplicates(scheduled)))
        )
    missing_from_waves = task_ids - set(scheduled)
    if missing_from_waves:
        errors.append(
            "tasks missing from waves: " + ", ".join(sorted(missing_from_waves))
        )

    if not any(task.get("role") == "integration" for task in task_by_id.values()):
        errors.append("plan requires an integration task")
    if not any(
        task.get("role") in {"review", "audit"}
        for task in task_by_id.values()
    ):
        errors.append("plan requires an independent review or audit task")

    if plan["strategy"] == "parallel-wave" and not any(
        wave.get("mode") == "parallel" for wave in waves if isinstance(wave, dict)
    ):
        errors.append("parallel-wave requires at least one parallel wave")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a portfolio multi-agent implementation plan."
    )
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()

    try:
        payload = json.loads(args.plan.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: plan not found: {args.plan}")
        return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read plan: {exc}")
        return 1

    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: multi-agent implementation plan is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
