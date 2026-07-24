"""Validate the minimum content-package contract without cloud services."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def validate(package: dict) -> list[str]:
    errors: list[str] = []
    required = {"schema_version", "source_facts", "evidence", "open_questions", "approved_copy", "handoff"}
    errors.extend(f"missing top-level field: {key}" for key in sorted(required - package.keys()))
    if package.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    facts = package.get("source_facts", {})
    for section in ("basics", "work", "education", "projects", "skills", "links"):
        if section not in facts:
            errors.append(f"source_facts missing section: {section}")
    for key, block in package.get("approved_copy", {}).items():
        if block.get("approval_status") != "user_approved":
            errors.append(f"approved_copy.{key} is not user approved")
        if not block.get("fact_ids"):
            errors.append(f"approved_copy.{key} has no fact_ids")
    handoff = package.get("handoff", {})
    if handoff.get("status") == "approved" and not package.get("approved_copy"):
        errors.append("approved handoff requires approved_copy")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    try:
        package = json.loads(args.package.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read package: {exc}", file=sys.stderr)
        return 1
    errors = validate(package)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("valid: resume content package schema_version=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
