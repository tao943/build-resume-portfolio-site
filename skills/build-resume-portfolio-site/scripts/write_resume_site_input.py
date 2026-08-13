"""Write an approved content package into the portfolio builder input boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

from validate_content_package import validate


def write_input(package_path: Path, workspace_root: Path, revision: int | None = None) -> list[Path]:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    errors = validate(package)
    if errors:
        raise ValueError("; ".join(errors))
    destination = workspace_root / ".resume-site-work" / "input"
    destination.mkdir(parents=True, exist_ok=True)
    existing = destination / "approved-copy.json"
    if existing.exists():
        current = json.loads(existing.read_text(encoding="utf-8"))
        if current.get("handoff", {}).get("status") == "approved" and revision is None:
            raise FileExistsError("approved-copy.json exists; pass --revision to create a new revision")
    next_revision = revision or int(package["handoff"].get("revision", 1))
    package["handoff"]["revision"] = next_revision
    package["handoff"]["status"] = "approved"
    files = {
        "source-manifest.json": {"schema_version": 1, "source_hashes": package["handoff"].get("source_hashes", [])},
        "normalized-resume.json": {"schema_version": 1, "source_facts": package["source_facts"], "evidence": package["evidence"]},
        "approved-copy.json": package,
        "..\\reports\\content-provenance.json": {
            "schema_version": 1,
            "package_revision": next_revision,
            "package_hash": hashlib.sha256(package_path.read_bytes()).hexdigest(),
            "evidence_count": len(package["evidence"]),
        },
    }
    written: list[Path] = []
    for relative, content in files.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(target)
        written.append(target)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument("--revision", type=int)
    args = parser.parse_args()
    try:
        for path in write_input(args.package, args.workspace_root, args.revision):
            print(path)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
