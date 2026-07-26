from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Sequence


CONFIRMATION_KEYS = {"prototype", "media_direction", "motion"}


def _validate_snapshot_reference(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    return (
        not path.is_absolute()
        and ".." not in path.parts
        and len(path.parts) >= 2
        and path.parts[0] == "versions"
    )


def migrate(state: dict) -> dict:
    if not isinstance(state, dict):
        raise ValueError("build state must be an object")
    if state.get("schema_version") != 3:
        raise ValueError("only schema_version 3 can migrate to 4")

    confirmations = state.get("confirmations")
    if not isinstance(confirmations, dict):
        raise ValueError("confirmations must be an object")
    if set(confirmations) != CONFIRMATION_KEYS or any(
        not isinstance(value, bool) for value in confirmations.values()
    ):
        raise ValueError("confirmations must contain boolean prototype, media_direction, and motion")

    confirmed_artifact = state.get("last_confirmed_artifact")
    if any(confirmations.values()) and not _validate_snapshot_reference(confirmed_artifact):
        raise ValueError("confirmed state requires a valid versions/ snapshot reference")
    if confirmed_artifact is not None and not _validate_snapshot_reference(confirmed_artifact):
        raise ValueError("last_confirmed_artifact must be null or a valid versions/ snapshot")

    migrated = dict(state)
    migrated["schema_version"] = 4
    migrated["skill_version"] = "1.2.0-react-vite"
    migrated["workflow_mode"] = (
        "fast-change-eligible" if confirmed_artifact else "full"
    )
    migrated["discovery"] = {
        "site_design_approved": False,
        "site_plan_validated": False,
    }
    return migrated


def migrate_file(source: Path, output: Path) -> None:
    source = source.resolve()
    output = output.resolve()
    if source == output:
        raise ValueError("output must differ from input")
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")

    try:
        state = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to read build state: {error}") from error
    migrated = migrate(state)

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(migrated, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temporary_path = Path(handle.name)
        os.replace(temporary_path, output)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Migrate a build-state.json file from schema version 3 to 4."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    try:
        migrate_file(args.source, args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"migration failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
