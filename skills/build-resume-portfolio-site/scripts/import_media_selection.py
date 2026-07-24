from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Sequence


SUPPORTED_FORMATS = {"jpg", "png", "webp", "gif"}


class SelectionError(RuntimeError):
    def __init__(self, message: str) -> None:
        self.category = "selection_invalid"
        super().__init__(f"selection_invalid: {message}")


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _read_manifest(workspace: Path, manifest_path: Path) -> tuple[dict[str, object], Path]:
    media_root = (workspace / ".resume-site-work" / "media-search").resolve()
    resolved_manifest = manifest_path.resolve()
    if (
        not _is_within(resolved_manifest, media_root)
        or resolved_manifest.name != "manifest.json"
        or not resolved_manifest.is_file()
        or resolved_manifest.is_symlink()
    ):
        raise SelectionError("manifest must be a regular APIHz search manifest inside the workspace")
    try:
        manifest = json.loads(resolved_manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SelectionError("manifest is unreadable or malformed") from exc
    if not isinstance(manifest, dict):
        raise SelectionError("manifest must be a JSON object")
    if manifest.get("schema_version") != 1 or manifest.get("provider") != "apihz":
        raise SelectionError("manifest schema or provider is unsupported")
    search_id = manifest.get("search_id")
    if not isinstance(search_id, str) or resolved_manifest.parent.name != search_id:
        raise SelectionError("manifest search ID does not match its directory")
    return manifest, resolved_manifest


def _candidate_source(manifest_path: Path, candidate: dict[str, object]) -> tuple[Path, str]:
    candidate_id = candidate.get("id")
    media_format = candidate.get("format")
    preview_path = candidate.get("preview_path")
    if (
        not isinstance(candidate_id, str)
        or not candidate_id.startswith("media-")
        or not isinstance(media_format, str)
        or media_format not in SUPPORTED_FORMATS
        or not isinstance(preview_path, str)
    ):
        raise SelectionError("candidate metadata is invalid")
    relative = PurePosixPath(preview_path)
    if relative.is_absolute() or ".." in relative.parts or len(relative.parts) != 2 or relative.parts[0] != "candidates":
        raise SelectionError("candidate path escapes its search directory")
    source = (manifest_path.parent / Path(*relative.parts)).resolve()
    candidates_root = (manifest_path.parent / "candidates").resolve()
    if (
        not _is_within(source, candidates_root)
        or not source.is_file()
        or source.is_symlink()
        or source.suffix.lower() != f".{media_format}"
    ):
        raise SelectionError("candidate file is missing, linked, or has the wrong format")
    return source, media_format


def _verify_candidate(manifest_path: Path, candidate: dict[str, object]) -> tuple[Path, str]:
    source, media_format = _candidate_source(manifest_path, candidate)
    payload = source.read_bytes()
    expected_size = candidate.get("byte_size")
    expected_hash = candidate.get("sha256")
    if (
        not isinstance(expected_size, int)
        or expected_size != len(payload)
        or not isinstance(expected_hash, str)
        or hashlib.sha256(payload).hexdigest() != expected_hash
    ):
        raise SelectionError("candidate changed after the search manifest was created")
    return source, media_format


def _atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise SelectionError("destination must not be a symbolic link")
    temporary = destination.with_suffix(destination.suffix + ".part")
    try:
        with source.open("rb") as reader, temporary.open("wb") as writer:
            shutil.copyfileobj(reader, writer, length=64 * 1024)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def _read_existing_report(report_path: Path) -> list[dict[str, object]]:
    if not report_path.exists():
        return []
    if report_path.is_symlink():
        raise SelectionError("selection report must not be a symbolic link")
    try:
        value = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SelectionError("existing selection report is malformed") from exc
    assets = value.get("assets") if isinstance(value, dict) else None
    if not isinstance(assets, list) or any(not isinstance(item, dict) for item in assets):
        raise SelectionError("existing selection report has an invalid asset list")
    return assets


def _atomic_write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise SelectionError("selection report must not be a symbolic link")
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def import_selected_media(
    workspace_root: Path,
    manifest_path: Path,
    candidate_ids: Sequence[str],
    *,
    updated_at: str | None = None,
) -> dict[str, object]:
    workspace = workspace_root.resolve()
    selected_ids = tuple(dict.fromkeys(item.strip() for item in candidate_ids if item.strip()))
    if not selected_ids:
        raise SelectionError("select at least one candidate ID")

    manifest, resolved_manifest = _read_manifest(workspace, manifest_path)
    raw_candidates = manifest.get("candidates")
    if not isinstance(raw_candidates, list) or any(not isinstance(item, dict) for item in raw_candidates):
        raise SelectionError("manifest candidate list is invalid")
    by_id: dict[str, dict[str, object]] = {}
    for candidate in raw_candidates:
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str) or candidate_id in by_id:
            raise SelectionError("manifest contains an invalid or duplicate candidate ID")
        by_id[candidate_id] = candidate
    if any(candidate_id not in by_id for candidate_id in selected_ids):
        raise SelectionError("selection contains an unknown candidate ID")

    destination_root = (
        workspace
        / ".resume-site-work"
        / "site"
        / "public"
        / "assets"
        / "external"
    ).resolve()
    report_path = workspace / ".resume-site-work" / "reports" / "media-selection.json"
    existing_assets = _read_existing_report(report_path)
    merged: dict[str, dict[str, object]] = {}
    order: list[str] = []
    for item in existing_assets:
        candidate_id = item.get("candidate_id")
        if isinstance(candidate_id, str) and candidate_id not in merged:
            merged[candidate_id] = item
            order.append(candidate_id)

    for candidate_id in selected_ids:
        candidate = by_id[candidate_id]
        source, media_format = _verify_candidate(resolved_manifest, candidate)
        destination = destination_root / f"{candidate_id}.{media_format}"
        if not _is_within(destination, destination_root):
            raise SelectionError("destination path escapes the React project")
        _atomic_copy(source, destination)
        item = {
            "candidate_id": candidate_id,
            "provider": "apihz",
            "asset_type": candidate.get("asset_type"),
            "project_path": f"/assets/external/{destination.name}",
            "source_url": candidate.get("source_url"),
            "sha256": candidate.get("sha256"),
            "rights_note": candidate.get("rights_note"),
        }
        if candidate_id not in merged:
            order.append(candidate_id)
        merged[candidate_id] = item

    timestamp = updated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    report: dict[str, object] = {
        "schema_version": 1,
        "updated_at": timestamp,
        "assets": [merged[candidate_id] for candidate_id in order],
    }
    _atomic_write_json(report_path, report)
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import user-selected APIHz media into a React project")
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--select", required=True, help="Comma-separated candidate IDs")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = import_selected_media(
            Path(args.workspace_root),
            Path(args.manifest),
            tuple(item.strip() for item in args.select.split(",")),
        )
    except SelectionError as exc:
        print(json.dumps({"ok": False, "category": exc.category}))
        return 2
    print(
        json.dumps(
            {
                "ok": True,
                "project_paths": [item["project_path"] for item in report["assets"]],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
