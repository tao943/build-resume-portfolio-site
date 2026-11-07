"""Build a reproducible, standalone SkillPay ZIP from runtime resources only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

RUNTIME_DIRS = {"agents", "assets", "prompts", "references", "scripts", "vendor"}
SKIP_DIRS = {"__pycache__", "node_modules", "dist", "tests"}
PRIVATE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".pyc", ".pyo"}


def package_skill(skill_root: Path, output: Path) -> dict:
    skill_root = skill_root.resolve()
    output = output.resolve()
    if not (skill_root / "SKILL.md").is_file():
        raise ValueError("SKILL.md is required")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    if output.is_relative_to(skill_root):
        raise ValueError("Place the release outside the Skill directory")
    files: list[Path] = []
    for path in sorted(skill_root.rglob("*")):
        relative = path.relative_to(skill_root)
        if any(part.startswith(".") or part in SKIP_DIRS for part in relative.parts):
            continue
        if relative.parts[0] not in RUNTIME_DIRS and relative.as_posix() != "SKILL.md":
            continue
        if path.is_symlink():
            raise ValueError(f"Symlinks are not distributable: {relative}")
        if not path.is_file() or path.name.startswith("test_") or path.suffix.lower() in PRIVATE_SUFFIXES:
            continue
        files.append(path)
    entries = []
    for path in files:
        raw = path.read_bytes()
        entries.append((path.relative_to(skill_root).as_posix(), raw))
    if sum(len(raw) for _, raw in entries) > 20 * 1024 * 1024:
        raise ValueError("Runtime resources exceed the platform's 20 MB limit")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, raw in entries:
                info = zipfile.ZipInfo(f"{skill_root.name}/{name}", date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, raw)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return {
        "file": str(output), "files": len(entries), "bytes": output.stat().st_size,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        result = package_skill(args.skill_root, args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
