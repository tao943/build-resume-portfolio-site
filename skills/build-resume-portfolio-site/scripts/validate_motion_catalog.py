from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence


EXPECTED_RECIPE_IDS = (
    "minimalist-3d-ribbon",
    "dark-portfolio-stack",
    "cinematic-travel",
    "editorial-healthcare",
    "outdoor-video-mask",
    "creator-portfolio",
    "vex-video-hero",
    "securify-typography",
    "neural-kinetics",
    "biotech-video",
    "assist-floating-cards",
)
ALLOWED_MEDIA_REQUIREMENTS = {"none", "optional", "preferred"}
ALLOWED_LAYERS = {"background", "content_media", "decorative"}
ALLOWED_FITS = {"cover", "contain", "masked"}
REQUIRED_PRESERVE_RULES = {
    "resume_facts",
    "section_order",
    "palette",
    "typography",
    "responsive_hierarchy",
    "confirmed_media_direction_baseline",
}


@dataclass(frozen=True)
class CatalogReport:
    ok: bool
    ready: bool
    recipe_ids: tuple[str, ...]
    errors: tuple[str, ...]


def validate_catalog(catalog_root: Path, require_ready: bool = True) -> CatalogReport:
    errors: list[str] = []
    manifest_path = catalog_root / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return CatalogReport(False, False, (), (f"invalid_manifest: {error}",))

    entries = manifest.get("recipes")
    if manifest.get("schema_version") != 1:
        errors.append("invalid_schema_version")
    if not isinstance(entries, list):
        return CatalogReport(False, False, (), ("invalid_recipe_entries",))

    recipe_ids = tuple(
        str(entry.get("id")) for entry in entries if isinstance(entry, dict)
    )
    if recipe_ids != EXPECTED_RECIPE_IDS:
        errors.append("invalid_recipe_ids")

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"invalid_manifest_entry: {index}")
            continue
        recipe_id = str(entry.get("id", ""))
        relative = str(entry.get("path", "")).replace("\\", "/")
        pure = PurePosixPath(relative)
        if not relative or pure.is_absolute() or ".." in pure.parts:
            errors.append(f"invalid_recipe_path: {relative}")
            continue
        try:
            recipe = json.loads((catalog_root / Path(relative)).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            errors.append(f"invalid_recipe: {recipe_id}: {error}")
            continue
        if recipe.get("schema_version") != 1:
            errors.append(f"invalid_recipe_schema: {recipe_id}")
        if recipe.get("id") != recipe_id:
            errors.append(f"recipe_id_mismatch: {recipe_id}")
        if recipe.get("source_id") != entry.get("source_id"):
            errors.append(f"source_id_mismatch: {recipe_id}")
        if recipe.get("primary_slot") not in {
            "hero_ambient",
            "hero_background",
            "hero_content_media",
        }:
            errors.append(f"invalid_primary_slot: {recipe_id}")
        media = recipe.get("media")
        if not isinstance(media, dict):
            errors.append(f"missing_media: {recipe_id}")
            continue
        if media.get("requirement") not in ALLOWED_MEDIA_REQUIREMENTS:
            errors.append(f"invalid_media_requirement: {recipe_id}")
        placement = media.get("placement_reference")
        if not isinstance(placement, dict):
            errors.append(f"missing_placement_reference: {recipe_id}")
        else:
            if placement.get("layer") not in ALLOWED_LAYERS:
                errors.append(f"invalid_placement_layer: {recipe_id}")
            if placement.get("fit") not in ALLOWED_FITS:
                errors.append(f"invalid_placement_fit: {recipe_id}")
            if not placement.get("description"):
                errors.append(f"missing_placement_description: {recipe_id}")
        playback = media.get("playback")
        if not isinstance(playback, dict) or playback.get("mode") != "passive_loop":
            errors.append(f"invalid_playback_mode: {recipe_id}")
        elif (
            playback.get("scroll_linked") is not False
            or playback.get("pointer_linked") is not False
        ):
            errors.append(f"interactive_video_forbidden: {recipe_id}")
        preserve = recipe.get("preserve")
        if not isinstance(preserve, list) or not REQUIRED_PRESERVE_RULES.issubset(preserve):
            errors.append(f"missing_preserve_rules: {recipe_id}")

    structurally_ok = not errors
    ready = (
        structurally_ok
        and manifest.get("catalog_status") == "ready"
        and manifest.get("catalog_version") == 1
    )
    if require_ready and structurally_ok and not ready:
        errors.append("resource_not_ready: motion-catalog")
    return CatalogReport(not errors, ready, recipe_ids, tuple(errors))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the motion recipe catalog")
    parser.add_argument("--catalog-root", type=Path, required=True)
    parser.add_argument("--allow-unready", action="store_true")
    args = parser.parse_args(argv)
    report = validate_catalog(args.catalog_root, require_ready=not args.allow_unready)
    print(json.dumps({"ok": report.ok, "ready": report.ready, "recipe_count": len(report.recipe_ids), "errors": report.errors}, ensure_ascii=False))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
