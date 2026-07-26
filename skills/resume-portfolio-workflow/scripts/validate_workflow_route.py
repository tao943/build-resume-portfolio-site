from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROUTES = {"content-full", "site-full", "site-fast-change"}
CONTENT_STATUSES = {"missing", "invalid", "draft", "ready"}
REQUIRED = {
    "schema_version",
    "route",
    "reason",
    "content_package_status",
    "confirmed_artifact",
    "strategic_scope_changed",
    "structural_scope_changed",
    "affected_files",
    "verification",
    "rollback_baseline",
}


def _non_empty_strings(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def validate(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["route report must be a JSON object"]

    errors = [
        f"missing field: {name}"
        for name in sorted(REQUIRED - set(payload))
    ]
    if errors:
        return errors

    if payload["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if payload["route"] not in ROUTES:
        errors.append("unsupported route")
    if payload["content_package_status"] not in CONTENT_STATUSES:
        errors.append("unsupported content_package_status")
    if not isinstance(payload["reason"], str) or not payload["reason"].strip():
        errors.append("reason must be a non-empty string")
    if not isinstance(payload["strategic_scope_changed"], bool):
        errors.append("strategic_scope_changed must be boolean")
    if not isinstance(payload["structural_scope_changed"], bool):
        errors.append("structural_scope_changed must be boolean")

    route = payload["route"]
    if route == "content-full" and payload["content_package_status"] == "ready":
        errors.append("content-full requires missing, invalid, or draft content")
    if route == "site-full" and payload["content_package_status"] != "ready":
        errors.append("site-full requires ready content")
    if route == "site-fast-change":
        if payload["content_package_status"] != "ready":
            errors.append("fast change requires ready content")
        if not payload["confirmed_artifact"]:
            errors.append("fast change requires a confirmed artifact")
        if payload["strategic_scope_changed"]:
            errors.append("strategic changes require the full workflow")
        if payload["structural_scope_changed"]:
            errors.append("structural changes require the full workflow")
        if not _non_empty_strings(payload["affected_files"]):
            errors.append("fast change requires affected files")
        if not _non_empty_strings(payload["verification"]):
            errors.append("fast change requires verification")
        if not payload["rollback_baseline"]:
            errors.append("fast change requires a rollback baseline")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a resume-portfolio workflow route."
    )
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.report.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: route report not found: {args.report}")
        return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read route report: {exc}")
        return 1
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: workflow route is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
