from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


FACT_SECTIONS = {"basics", "work", "education", "projects", "skills", "links"}
HASH_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


def _read_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, f"cannot read {path.name}: {exc}"


def _validate_package_shape(package: Any) -> list[str]:
    if not isinstance(package, dict):
        return ["approved-copy.json must contain a JSON object"]
    errors: list[str] = []
    required = {
        "schema_version",
        "source_facts",
        "evidence",
        "open_questions",
        "approved_copy",
        "handoff",
    }
    missing = required - set(package)
    if missing:
        errors.append("approved-copy.json missing: " + ", ".join(sorted(missing)))
        return errors
    if package["schema_version"] != 1:
        errors.append("approved-copy.json schema_version must be 1")
    facts = package["source_facts"]
    if not isinstance(facts, dict):
        errors.append("source_facts must be an object")
    else:
        missing_sections = FACT_SECTIONS - set(facts)
        if missing_sections:
            errors.append(
                "source_facts missing sections: "
                + ", ".join(sorted(missing_sections))
            )
    if not isinstance(package["approved_copy"], dict) or not package["approved_copy"]:
        errors.append("approved_copy must be a non-empty object")
    if not isinstance(package["handoff"], dict):
        errors.append("handoff must be an object")
    return errors


def validate_workspace(workspace_root: Path) -> tuple[int, list[str]]:
    work_root = workspace_root / ".resume-site-work"
    paths = {
        "manifest": work_root / "input" / "source-manifest.json",
        "normalized": work_root / "input" / "normalized-resume.json",
        "approved": work_root / "input" / "approved-copy.json",
        "provenance": work_root / "reports" / "content-provenance.json",
    }
    missing = [str(path.relative_to(workspace_root)) for path in paths.values() if not path.is_file()]
    if missing:
        return 2, ["missing handoff files: " + ", ".join(missing)]

    payloads: dict[str, Any] = {}
    read_errors: list[str] = []
    for key, path in paths.items():
        payload, error = _read_json(path)
        if error:
            read_errors.append(error)
        else:
            payloads[key] = payload
    if read_errors:
        return 1, read_errors

    package = payloads["approved"]
    shape_errors = _validate_package_shape(package)
    if shape_errors:
        return 1, shape_errors

    handoff = package["handoff"]
    if handoff.get("status") != "approved":
        return 2, ["handoff status is not approved"]

    errors: list[str] = []
    revision = handoff.get("revision")
    if not isinstance(revision, int) or revision < 1:
        errors.append("handoff revision must be a positive integer")

    for key, block in package["approved_copy"].items():
        if not isinstance(block, dict):
            errors.append(f"approved_copy.{key} must be an object")
            continue
        if block.get("approval_status") != "user_approved":
            errors.append(f"approved_copy.{key} is not user_approved")
        fact_ids = block.get("fact_ids")
        if not isinstance(fact_ids, list) or not fact_ids:
            errors.append(f"approved_copy.{key} has no fact_ids")

    manifest = payloads["manifest"]
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        errors.append("source-manifest.json schema_version must be 1")
    elif not isinstance(manifest.get("source_hashes"), list):
        errors.append("source-manifest.json source_hashes must be a list")
    elif manifest["source_hashes"] != handoff.get("source_hashes", []):
        errors.append("source_hashes mismatch between manifest and approved package")

    normalized = payloads["normalized"]
    if not isinstance(normalized, dict) or normalized.get("schema_version") != 1:
        errors.append("normalized-resume.json schema_version must be 1")
    else:
        if normalized.get("source_facts") != package["source_facts"]:
            errors.append("source_facts mismatch between normalized and approved package")
        if normalized.get("evidence") != package["evidence"]:
            errors.append("evidence mismatch between normalized and approved package")

    provenance = payloads["provenance"]
    if not isinstance(provenance, dict) or provenance.get("schema_version") != 1:
        errors.append("content-provenance.json schema_version must be 1")
    else:
        if provenance.get("package_revision") != revision:
            errors.append("package revision mismatch in content provenance")
        package_hash = provenance.get("package_hash")
        if not isinstance(package_hash, str) or not HASH_PATTERN.fullmatch(package_hash):
            errors.append("content provenance package_hash must be SHA-256")
        evidence = package["evidence"]
        expected_count = len(evidence) if isinstance(evidence, (list, dict)) else None
        if provenance.get("evidence_count") != expected_count:
            errors.append("evidence_count mismatch in content provenance")

    if errors:
        return 1, errors
    return 0, [f"approved content package revision={revision}"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the resume-content handoff before website work."
    )
    parser.add_argument("--workspace-root", required=True, type=Path)
    args = parser.parse_args()

    code, messages = validate_workspace(args.workspace_root.resolve())
    label = {0: "CONTENT_READY", 1: "CONTENT_INVALID", 2: "ROUTE_REQUIRED"}[code]
    for message in messages:
        print(f"{label}: {message}")
    return code


if __name__ == "__main__":
    sys.exit(main())
