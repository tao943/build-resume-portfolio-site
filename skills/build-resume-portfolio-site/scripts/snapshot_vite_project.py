from __future__ import annotations

import argparse
import json
import shutil
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


EXCLUDED_NAMES = {"node_modules", "dist", ".git", ".resume-site-work", "__pycache__"}


@dataclass(frozen=True)
class SnapshotReport:
    ok: bool
    operation: str
    source: str
    destination: str
    files_copied: int
    excluded_names: tuple[str, ...]


def _resolved(path: Path) -> Path:
    return path.expanduser().resolve()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _validate_non_overlapping(source: Path, destination: Path) -> None:
    if source == destination or _is_relative_to(destination, source) or _is_relative_to(source, destination):
        raise ValueError("source_and_destination_must_not_overlap")


def _ignore(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in EXCLUDED_NAMES}


def _copy_to_temporary(source: Path, destination: Path) -> tuple[Path, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.parent / f".{destination.name}.tmp-{uuid.uuid4().hex}"
    try:
        shutil.copytree(source, temporary, ignore=_ignore, copy_function=shutil.copy2)
        files_copied = sum(1 for path in temporary.rglob("*") if path.is_file())
        return temporary, files_copied
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise


def snapshot_project(source: Path, destination: Path) -> SnapshotReport:
    source = _resolved(source)
    destination = _resolved(destination)
    if not source.is_dir():
        raise FileNotFoundError(f"source_project_not_found: {source}")
    _validate_non_overlapping(source, destination)
    if destination.exists():
        raise FileExistsError(f"snapshot_already_exists: {destination}")

    temporary, files_copied = _copy_to_temporary(source, destination)
    try:
        temporary.replace(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return SnapshotReport(
        True,
        "snapshot",
        str(source),
        str(destination),
        files_copied,
        tuple(sorted(EXCLUDED_NAMES)),
    )


def restore_snapshot(snapshot: Path, destination: Path) -> SnapshotReport:
    snapshot = _resolved(snapshot)
    destination = _resolved(destination)
    if not snapshot.is_dir():
        raise FileNotFoundError(f"snapshot_not_found: {snapshot}")
    _validate_non_overlapping(snapshot, destination)

    temporary, files_copied = _copy_to_temporary(snapshot, destination)
    backup = destination.parent / f".{destination.name}.backup-{uuid.uuid4().hex}"
    moved_existing = False
    try:
        if destination.exists():
            destination.replace(backup)
            moved_existing = True
        temporary.replace(destination)
    except Exception:
        if destination.exists():
            shutil.rmtree(destination)
        if moved_existing and backup.exists():
            backup.replace(destination)
        raise
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
        if backup.exists():
            shutil.rmtree(backup)

    return SnapshotReport(
        True,
        "restore",
        str(snapshot),
        str(destination),
        files_copied,
        tuple(sorted(EXCLUDED_NAMES)),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Snapshot or restore a React + Vite source project.")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    for name in ("snapshot", "restore"):
        command = subparsers.add_parser(name)
        command.add_argument("source", type=Path)
        command.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    try:
        report = (
            snapshot_project(args.source, args.destination)
            if args.operation == "snapshot"
            else restore_snapshot(args.source, args.destination)
        )
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "operation": args.operation, "error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())