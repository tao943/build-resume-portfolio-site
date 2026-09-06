from __future__ import annotations

import argparse
import copy
import json
import uuid
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from validate_site_design_spec import validate


INVALIDATED_ARTIFACTS = ["design-intelligence", "creative-direction", "design-contract", "motion-plan", "visual-audit"]


def migrate(payload: Mapping[str, Any], reason: str) -> dict[str, Any]:
    if payload.get("schema_version") != 3:
        raise ValueError("migration requires schema version 3")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("migration reason is required")
    source_errors = validate(dict(payload))
    if source_errors:
        raise ValueError("source spec is invalid: " + "; ".join(source_errors))
    result = copy.deepcopy(dict(payload))
    previous = result["decisions"]["structure"]
    result["schema_version"] = 4
    result["decisions"]["structure"] = {
        "status": "agent_delegated",
        "priority": "visual-impact",
        "scope": "universal",
        "exploration_policy": "fit-novelty-wildcard",
        "direct_generation": True,
        "approval": copy.deepcopy(result["requirements_approval"]),
    }
    result["migration"] = {
        "source_schema_version": 3,
        "source_structure_candidate_ids": list(previous.get("selected_candidate_ids", [])),
        "reason": reason.strip(),
        "invalidated_artifacts": list(INVALIDATED_ARTIFACTS),
    }
    errors = validate(result)
    if errors:
        raise ValueError("migrated spec is invalid: " + "; ".join(errors))
    return result


def _atomic_write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Explicitly migrate site design spec v3 to Agent-delegated v4 structure.")
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.source.read_text(encoding="utf-8"))
        _atomic_write(args.output, migrate(payload, args.reason))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1
    print("OK: migrated site design spec from v3 to v4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
