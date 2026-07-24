from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
from dataclasses import asdict, dataclass
from math import gcd
from pathlib import Path
from typing import Any, Sequence


SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_PAGE_SIZE = 9
DEFAULT_THUMBNAIL_EDGE = 640


@dataclass(frozen=True)
class CatalogReport:
    ok: bool
    ready: bool
    changed: bool
    manifest_path: str
    contact_sheets: tuple[str, ...]
    valid_count: int
    duplicate_count: int
    warnings: tuple[str, ...]


def _load_pillow() -> tuple[Any, Any, Any, Any]:
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageOps
    except ImportError as error:
        raise RuntimeError(
            "Pillow is required for reference indexing. Run: python -m pip install Pillow"
        ) from error
    return Image, ImageDraw, ImageFont, ImageOps


def _resolved(path: Path) -> Path:
    return path.expanduser().resolve()


def _is_inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _validate_paths(source_dir: Path, destination: Path) -> None:
    if source_dir == destination or _is_inside(destination, source_dir) or _is_inside(source_dir, destination):
        raise ValueError("source_and_catalog_paths_must_not_overlap")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _ratio(width: int, height: int) -> str:
    factor = gcd(width, height)
    return f"{width // factor}:{height // factor}"


def _visual_tags(width: int, height: int) -> list[str]:
    value = width / height
    tags = ["square"] if 0.9 <= value <= 1.1 else ["landscape" if value > 1 else "portrait"]
    if value >= 1.5:
        tags.append("wide")
    if value <= 0.67:
        tags.append("tall")
    return tags


def _dhash(image: Any) -> int:
    gray = image.convert("L").resize((9, 8))
    value = 0
    for row in range(8):
        for column in range(8):
            value = (value << 1) | int(gray.getpixel((column, row)) > gray.getpixel((column + 1, row)))
    return value


def _hamming(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def _record_fingerprint(records: list[dict[str, Any]]) -> str:
    payload = [
        {
            "relative_path": item["relative_path"],
            "source_sha256": item["source_sha256"],
            "width": item["width"],
            "height": item["height"],
        }
        for item in records
    ]
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _font(image_font_module: Any) -> Any:
    try:
        return image_font_module.load_default()
    except Exception:
        return None


def _write_thumbnail(image: Any, image_module: Any, destination: Path, image_ops: Any, edge: int) -> None:
    thumbnail = image_ops.contain(image.convert("RGB"), (edge, edge))
    canvas = image_module.new("RGB", (edge, edge), (245, 244, 240))
    canvas.paste(thumbnail, ((edge - thumbnail.width) // 2, (edge - thumbnail.height) // 2))
    canvas.save(destination, format="WEBP", quality=88, method=6)


def _write_contact_sheets(
    records: list[dict[str, Any]],
    image_module: Any,
    image_draw_module: Any,
    image_font_module: Any,
    image_ops: Any,
    destination: Path,
    page_size: int,
) -> list[str]:
    columns = 3
    rows = (page_size + columns - 1) // columns
    cell_width, cell_height = 360, 300
    sheets: list[str] = []
    font = _font(image_font_module)
    for page_start in range(0, len(records), page_size):
        page_records = records[page_start : page_start + page_size]
        page_number = page_start // page_size + 1
        sheet = image_module.new("RGB", (columns * cell_width, rows * cell_height), (238, 238, 234))
        draw = image_draw_module.Draw(sheet)
        for index, record in enumerate(page_records):
            image = image_module.open(record["source_file"]).convert("RGB")
            preview = image_ops.contain(image, (cell_width - 24, cell_height - 56))
            left = (index % columns) * cell_width
            top = (index // columns) * cell_height
            x = left + (cell_width - preview.width) // 2
            y = top + 8 + (cell_height - 48 - preview.height) // 2
            sheet.paste(preview, (x, y))
            draw.rectangle((left + 4, top + 4, left + cell_width - 5, top + cell_height - 5), outline=(205, 205, 200), width=2)
            draw.text((left + 12, top + cell_height - 34), record["id"], fill=(30, 30, 30), font=font)
            image.close()
        filename = f"sheet-{page_number:03d}.webp"
        output_path = destination / filename
        sheet.save(output_path, format="WEBP", quality=88, method=6)
        sheets.append(f"contact-sheets/{filename}")
    return sheets


def _promote_temporary(temporary: Path, destination: Path) -> None:
    backup = destination.parent / f".{destination.name}.backup-{uuid.uuid4().hex}"
    moved = False
    try:
        if destination.exists():
            destination.replace(backup)
            moved = True
        temporary.replace(destination)
    except Exception:
        if destination.exists():
            shutil.rmtree(destination)
        if moved and backup.exists():
            backup.replace(destination)
        raise
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
        if backup.exists():
            shutil.rmtree(backup)


def index_reference_library(
    source_dir: Path,
    workspace_root: Path,
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
    thumbnail_edge: int = DEFAULT_THUMBNAIL_EDGE,
) -> CatalogReport:
    source_dir = _resolved(source_dir)
    workspace_root = _resolved(workspace_root)
    destination = workspace_root / ".resume-site-work" / "reference-library"
    manifest_path = destination / "manifest.json"
    if not source_dir.is_dir():
        raise FileNotFoundError(f"reference_source_not_found: {source_dir}")
    if page_size <= 0 or thumbnail_edge <= 0:
        raise ValueError("page_size_and_thumbnail_edge_must_be_positive")
    _validate_paths(source_dir, destination)
    image_module, image_draw_module, image_font_module, image_ops = _load_pillow()

    warnings: list[str] = []
    candidates: list[dict[str, Any]] = []
    for path in sorted(source_dir.rglob("*"), key=lambda item: item.relative_to(source_dir).as_posix().lower()):
        if path.is_symlink():
            warnings.append(f"skipped_symlink: {path.relative_to(source_dir).as_posix()}")
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            warnings.append(f"skipped_unsupported: {path.relative_to(source_dir).as_posix()}")
            continue
        relative_path = path.relative_to(source_dir).as_posix()
        try:
            source_hash = _sha256(path)
            with image_module.open(path) as probe:
                probe.verify()
            with image_module.open(path) as opened:
                rgb = opened.convert("RGB")
                width, height = rgb.size
                image_hash = _dhash(rgb)
        except Exception as error:
            warnings.append(f"skipped_invalid: {relative_path}: {error}")
            continue
        candidates.append(
            {
                "source_file": path,
                "relative_path": relative_path,
                "source_sha256": source_hash,
                "width": width,
                "height": height,
                "dhash": image_hash,
            }
        )

    if not candidates:
        return CatalogReport(False, False, False, str(manifest_path), (), 0, 0, tuple(warnings))

    by_hash: dict[str, dict[str, Any]] = {}
    duplicate_count = 0
    for candidate in candidates:
        identifier = "ref-" + candidate["source_sha256"][:8]
        candidate["id"] = identifier
        canonical = by_hash.get(candidate["source_sha256"])
        if canonical:
            candidate["selectable"] = False
            candidate["duplicate_of"] = canonical["id"]
            duplicate_count += 1
        else:
            candidate["selectable"] = True
            candidate["duplicate_of"] = None
            by_hash[candidate["source_sha256"]] = candidate

    near_duplicates: list[dict[str, Any]] = []
    for index, left in enumerate(candidates):
        if not left["selectable"]:
            continue
        for right in candidates[index + 1 :]:
            if not right["selectable"]:
                continue
            distance = _hamming(left["dhash"], right["dhash"])
            if distance <= 6:
                near_duplicates.append({"left": left["id"], "right": right["id"], "dhash_distance": distance})

    fingerprint = _record_fingerprint(candidates)
    previous: dict[str, Any] = {}
    if manifest_path.is_file():
        try:
            previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            previous = {}
    changed = previous.get("catalog_fingerprint") != fingerprint
    previous_version = previous.get("library_version")
    version = previous_version if not changed and isinstance(previous_version, int) else (previous_version + 1 if isinstance(previous_version, int) else 1)

    temporary = destination.parent / f".{destination.name}.tmp-{uuid.uuid4().hex}"
    try:
        (temporary / "thumbnails").mkdir(parents=True)
        (temporary / "contact-sheets").mkdir()
        records: list[dict[str, Any]] = []
        for candidate in candidates:
            if candidate["selectable"]:
                with image_module.open(candidate["source_file"]) as opened:
                    _write_thumbnail(opened, image_module, temporary / "thumbnails" / f"{candidate['id']}.webp", image_ops, thumbnail_edge)
            records.append(
                {
                    "id": candidate["id"],
                    "path": f"thumbnails/{candidate['id']}.webp",
                    "source_path": candidate["source_file"].resolve().as_posix(),
                    "source_sha256": candidate["source_sha256"],
                    "width": candidate["width"],
                    "height": candidate["height"],
                    "aspect_ratio": _ratio(candidate["width"], candidate["height"]),
                    "role_tags": [],
                    "visual_tags": _visual_tags(candidate["width"], candidate["height"]),
                    "usage_scope": "style_only",
                    "source_note": "user-provided local reference",
                    "license_note": "rights not verified; private style analysis only",
                    "available": True,
                    "selectable": candidate["selectable"],
                    "duplicate_of": candidate["duplicate_of"],
                }
            )
        selectable = [candidate for candidate in candidates if candidate["selectable"]]
        contact_sheets = _write_contact_sheets(
            selectable,
            image_module,
            image_draw_module,
            image_font_module,
            image_ops,
            temporary / "contact-sheets",
            page_size,
        )
        manifest = {
            "schema_version": 1,
            "library_status": "ready",
            "library_version": version,
            "catalog_fingerprint": fingerprint,
            "source_root": source_dir.as_posix(),
            "contact_sheets": contact_sheets,
            "references": records,
        }
        (temporary / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        duplicate_report = {
            "schema_version": 1,
            "exact_duplicate_count": duplicate_count,
            "exact_groups": [
                {"canonical": canonical["id"], "duplicates": [item["id"] for item in candidates if item["duplicate_of"] == canonical["id"]]}
                for canonical in by_hash.values()
                if any(item["duplicate_of"] == canonical["id"] for item in candidates)
            ],
            "near_duplicate_candidates": near_duplicates,
        }
        (temporary / "duplicate-report.json").write_text(json.dumps(duplicate_report, ensure_ascii=False, indent=2), encoding="utf-8")
        _promote_temporary(temporary, destination)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise

    absolute_sheets = tuple(str(destination / item) for item in contact_sheets)
    return CatalogReport(True, True, changed, str(manifest_path), absolute_sheets, len(candidates), duplicate_count, tuple(warnings))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Index a private visual reference library for the portfolio Skill.")
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--workspace-root", type=Path, default=Path.cwd())
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument("--thumbnail-edge", type=int, default=DEFAULT_THUMBNAIL_EDGE)
    args = parser.parse_args(argv)
    try:
        report = index_reference_library(
            args.source_dir,
            args.workspace_root,
            page_size=args.page_size,
            thumbnail_edge=args.thumbnail_edge,
        )
    except RuntimeError as error:
        print(json.dumps({"ok": False, "ready": False, "error": str(error)}, ensure_ascii=False, indent=2))
        return 2
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "ready": False, "error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    return 0 if report.ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
