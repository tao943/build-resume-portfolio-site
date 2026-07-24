from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path, PurePosixPath
from typing import NamedTuple


CATALOG_VERSION_PATTERN = re.compile(r"^- Catalog-Version:\s*(\S+)\s*$", re.MULTILINE)
MANIFEST_LINE_PATTERN = re.compile(r"^([0-9a-f]{64})  (.+)$")
EXPECTED_COPYRIGHT = "Copyright (c) 2024 Next Level Builder"

REQUIRED_HASHED_FILES = (
    "LICENSE",
    "UPSTREAM.md",
    "data/styles.csv",
    "data/colors.csv",
    "data/typography.csv",
    "data/landing.csv",
    "data/products.csv",
    "data/ui-reasoning.csv",
    "data/ux-guidelines.csv",
    "data/motion.csv",
    "data/stacks/react.csv",
    "src/core.py",
)

REQUIRED_CSV_COLUMNS = {
    "data/styles.csv": {"Style Category", "Keywords", "Best For", "AI Prompt Keywords"},
    "data/colors.csv": {"Product Type", "Primary", "Background", "Foreground"},
    "data/typography.csv": {"Font Pairing Name", "Heading Font", "Body Font", "Best For"},
    "data/landing.csv": {"Pattern Name", "Keywords", "Section Order"},
    "data/products.csv": {"Product Type", "Keywords", "Primary Style Recommendation"},
    "data/ui-reasoning.csv": {"UI_Category", "Recommended_Pattern", "Decision_Rules"},
    "data/ux-guidelines.csv": {"Category", "Issue", "Description", "Severity"},
    "data/motion.csv": {"Category", "Intensity Tier", "Keywords", "Trigger"},
    "data/stacks/react.csv": {"Category", "Guideline", "Description", "Severity"},
}


class CatalogReport(NamedTuple):
    ok: bool
    catalog_version: str | None
    checked_files: tuple[str, ...]
    errors: tuple[str, ...]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_manifest(path: Path) -> tuple[dict[str, str], list[str]]:
    entries: dict[str, str] = {}
    errors: list[str] = []
    if not path.is_file():
        return entries, ["missing_manifest"]
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as error:
        return entries, [f"invalid_manifest: {error}"]
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        match = MANIFEST_LINE_PATTERN.fullmatch(line)
        if match is None:
            errors.append(f"invalid_manifest_line: {line_number}")
            continue
        digest, relative = match.groups()
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or relative != pure.as_posix():
            errors.append(f"invalid_manifest_path: {relative}")
            continue
        if relative in entries:
            errors.append(f"duplicate_manifest_path: {relative}")
            continue
        entries[relative] = digest
    return entries, errors


def validate_catalog(catalog_root: Path, require_hashes: bool = True) -> CatalogReport:
    root = catalog_root.resolve()
    errors: list[str] = []
    checked: list[str] = []

    license_path = root / "LICENSE"
    upstream_path = root / "UPSTREAM.md"
    if not license_path.is_file():
        errors.append("missing_license")
    else:
        try:
            license_text = license_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"invalid_license: {error}")
        else:
            if "MIT License" not in license_text or EXPECTED_COPYRIGHT not in license_text:
                errors.append("invalid_license_notice")

    catalog_version: str | None = None
    if not upstream_path.is_file():
        errors.append("missing_upstream_record")
    else:
        try:
            upstream_text = upstream_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"invalid_upstream_record: {error}")
        else:
            version_match = CATALOG_VERSION_PATTERN.search(upstream_text)
            if version_match is None:
                errors.append("missing_catalog_version")
            else:
                catalog_version = version_match.group(1)
            if EXPECTED_COPYRIGHT not in upstream_text:
                errors.append("missing_upstream_copyright")

    manifest, manifest_errors = _read_manifest(root / "MANIFEST.sha256")
    errors.extend(manifest_errors)
    for relative in REQUIRED_HASHED_FILES:
        path = root / Path(relative)
        if not path.is_file():
            errors.append(f"missing_catalog_file: {relative}")
            continue
        checked.append(relative)
        if require_hashes:
            expected = manifest.get(relative)
            if expected is None:
                errors.append(f"missing_manifest_entry: {relative}")
            elif _sha256(path) != expected:
                errors.append(f"hash_mismatch: {relative}")

    errors.extend(
        f"unexpected_manifest_entry: {relative}"
        for relative in sorted(set(manifest) - set(REQUIRED_HASHED_FILES))
    )

    for relative, required_columns in REQUIRED_CSV_COLUMNS.items():
        path = root / Path(relative)
        if not path.is_file():
            continue
        try:
            with path.open("r", encoding="utf-8", newline="") as handle:
                header = next(csv.reader(handle), [])
        except (OSError, UnicodeError, csv.Error) as error:
            errors.append(f"invalid_csv: {relative}: {error}")
            continue
        missing = sorted(required_columns - set(header))
        if missing:
            errors.append(f"invalid_csv_header: {relative}: {','.join(missing)}")

    return CatalogReport(
        ok=not errors,
        catalog_version=catalog_version,
        checked_files=tuple(checked),
        errors=tuple(errors),
    )


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Validate the vendored UI/UX design catalog.")
    parser.add_argument("catalog_root", type=Path)
    args = parser.parse_args()
    report = validate_catalog(args.catalog_root)
    print(json.dumps(report._asdict(), ensure_ascii=False, indent=2))
    raise SystemExit(0 if report.ok else 1)
