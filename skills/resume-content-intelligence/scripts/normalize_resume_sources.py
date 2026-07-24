"""Normalize extracted source records without inventing resume facts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def normalize(input_dir: Path) -> dict:
    records = []
    for path in sorted(input_dir.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() not in {".pdf", ".docx", ".md", ".txt"}:
            continue
        relative = path.relative_to(input_dir).as_posix()
        source_id = "source-" + hashlib.sha256(relative.encode("utf-8")).hexdigest()[:12]
        records.append({
            "source_id": source_id,
            "relative_path": relative,
            "file_name": path.name,
            "extension": path.suffix.lower(),
            "status": "pending_extraction",
        })
    return {"schema_version": 1, "sources": records}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(normalize(args.input_dir), indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
