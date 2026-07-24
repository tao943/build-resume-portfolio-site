from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


REQUIRED_PRESERVE = {
    "resume_facts",
    "section_order",
    "palette",
    "typography",
    "responsive_hierarchy",
    "confirmed_media_direction_baseline",
}


@dataclass(frozen=True)
class PlanReport:
    ok: bool
    errors: tuple[str, ...]


def _string_list(value: object) -> list[str] | None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return value


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_motion_item(item: object) -> bool:
    if not isinstance(item, dict):
        return False
    controllers = _string_list(item.get("controllers"))
    dependencies = _string_list(item.get("dependencies"))
    return (
        all(_nonempty_string(item.get(field)) for field in ("id", "source", "target", "purpose", "cleanup", "mobile", "reduced_motion", "fallback"))
        and controllers is not None
        and bool(controllers)
        and all(controller.strip() for controller in controllers)
        and dependencies is not None
        and isinstance(item.get("conflict_resolution"), str)
    )


def validate_selection(data: object, recipe_ids: frozenset[str]) -> PlanReport:
    if not isinstance(data, dict):
        return PlanReport(False, ("selection_must_be_object",))
    errors: list[str] = []
    primary = _string_list(data.get("primary_recipe_ids"))
    secondary = _string_list(data.get("secondary_effect_ids"))
    if primary is None:
        errors.append("invalid_primary_recipe_ids")
        primary = []
    if secondary is None:
        errors.append("invalid_secondary_effect_ids")
        secondary = []
    selected_ids = primary + secondary
    for recipe_id in selected_ids:
        if recipe_id not in recipe_ids:
            errors.append(f"unknown_recipe: {recipe_id}")
    for recipe_id in sorted({recipe_id for recipe_id in selected_ids if selected_ids.count(recipe_id) > 1}):
        errors.append(f"duplicate_recipe_id: {recipe_id}")

    items = data.get("items")
    if not isinstance(items, list):
        errors.append("invalid_motion_items")
        items = []
    item_ids: list[str] = []
    for item in items:
        item_id = item.get("id") if isinstance(item, dict) else None
        display_id = item_id if isinstance(item_id, str) else "unknown"
        if not _valid_motion_item(item):
            errors.append(f"invalid_motion_item: {display_id}")
            continue
        item_ids.append(item_id)
    for item_id in sorted({item_id for item_id in item_ids if item_ids.count(item_id) > 1}):
        errors.append(f"duplicate_motion_item_id: {item_id}")
    if set(item_ids) != set(selected_ids) or len(item_ids) != len(selected_ids):
        errors.append("selection_items_must_match_recipe_ids")

    owners: dict[tuple[str, str], list[dict[str, object]]] = {}
    for item in items:
        if not _valid_motion_item(item):
            continue
        for controller in item["controllers"]:
            owners.setdefault((item["target"], controller), []).append(item)
    for (target, controller), conflicting_items in owners.items():
        if len(conflicting_items) > 1 and not any(
            _nonempty_string(item.get("conflict_resolution")) for item in conflicting_items
        ):
            errors.append(f"unresolved_selection_conflict: {target}:{controller}")
    preserve = _string_list(data.get("preserve"))
    if preserve is None or not REQUIRED_PRESERVE.issubset(preserve):
        errors.append("missing_preserve_rules")
    return PlanReport(not errors, tuple(errors))


def validate_media_slot(data: object, recipe: dict[str, object]) -> PlanReport:
    if not isinstance(data, dict):
        return PlanReport(False, ("media_slot_must_be_object",))
    errors: list[str] = []
    if data.get("recipe_id") != recipe.get("id"):
        errors.append("recipe_id_mismatch")
    if not isinstance(data.get("placement_reference"), dict):
        errors.append("missing_placement_reference")
    resolved = data.get("resolved_placement")
    if not isinstance(resolved, dict) or not resolved:
        errors.append("missing_resolved_placement")
    playback = data.get("playback")
    if not isinstance(playback, dict) or playback.get("mode") != "passive_loop":
        errors.append("invalid_playback_mode")
    elif playback.get("scroll_linked") is not False or playback.get("pointer_linked") is not False:
        errors.append("interactive_video_forbidden")
    preserve = _string_list(data.get("preserve"))
    if preserve is None or not REQUIRED_PRESERVE.issubset(preserve):
        errors.append("missing_preserve_rules")
    return PlanReport(not errors, tuple(errors))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate motion selection or media slot JSON")
    subparsers = parser.add_subparsers(dest="mode", required=True)
    selection = subparsers.add_parser("selection")
    selection.add_argument("data", type=Path)
    selection.add_argument("--recipe-id", action="append", default=[])
    slot = subparsers.add_parser("slot")
    slot.add_argument("data", type=Path)
    slot.add_argument("recipe", type=Path)
    args = parser.parse_args(argv)
    data = json.loads(args.data.read_text(encoding="utf-8"))
    if args.mode == "selection":
        report = validate_selection(data, frozenset(args.recipe_id))
    else:
        recipe = json.loads(args.recipe.read_text(encoding="utf-8"))
        report = validate_media_slot(data, recipe)
    print(json.dumps(asdict(report), ensure_ascii=False))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
