from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


REPORT_FIELDS = frozenset({
    "schema_version", "design_read", "visual_thesis", "energy_curve", "image_analysis",
    "internal_directions", "selected_direction_id", "selection_reason", "section_directions",
    "interaction_compatibility", "media_upgrades", "responsive_strategy",
    "reduced_motion_strategy", "implementation_choices", "preserve",
})
TEXT_REPORT_FIELDS = frozenset({
    "visual_thesis", "selected_direction_id", "selection_reason",
})
LIST_REPORT_FIELDS = frozenset({
    "energy_curve", "image_analysis", "internal_directions", "section_directions",
    "interaction_compatibility", "media_upgrades", "implementation_choices", "preserve",
})
CONTROLLER_TYPES = frozenset({"scroll", "pointer", "drag", "camera", "video_progress", "transform", "filter"})
COMPARISON_FIELDS = ("beauty", "content", "narrative", "coherence", "device", "risk")


@dataclass(frozen=True)
class MediaDirectionValidationReport:
    ok: bool
    errors: tuple[str, ...]


def _add_once(errors: list[str], value: str) -> None:
    if value not in errors:
        errors.append(value)


def _text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split())
    return normalized or None


def _text_list(value: object, minimum: int = 0) -> list[str] | None:
    if not isinstance(value, list) or len(value) < minimum:
        return None
    normalized = [_text(item) for item in value]
    return normalized if all(item is not None for item in normalized) else None


def _structured_text_object(
    value: object, fields: frozenset[str], label: str, errors: list[str]
) -> None:
    if not isinstance(value, dict):
        _add_once(errors, f"invalid_{label}")
        return
    _unexpected_fields(value, fields, label, errors)
    _required_fields(value, fields, label, errors)
    for field in fields:
        if _text(value.get(field)) is None:
            _add_once(errors, f"invalid_{label}_{field}")


def _unexpected_fields(data: dict[str, object], allowed: frozenset[str], label: str, errors: list[str]) -> None:
    for field in sorted(data.keys() - allowed):
        _add_once(errors, f"unexpected_{label}_field: {field}")


def _required_fields(data: dict[str, object], required: frozenset[str], label: str, errors: list[str]) -> None:
    for field in sorted(required - data.keys()):
        _add_once(errors, f"missing_{label}_field: {field}")


def _read_json(path: Path, label: str, errors: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        _add_once(errors, f"{label}_not_found")
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        _add_once(errors, f"invalid_{label}_json: {error}")
    return None


def _load_inventory(path: Path, errors: list[str]) -> dict[str, tuple[str, frozenset[str]]]:
    data = _read_json(path, "media_inventory", errors)
    if not isinstance(data, dict):
        if data is not None:
            _add_once(errors, "media_inventory_must_be_object")
        return {}
    allowed = frozenset({"schema_version", "assets"})
    _unexpected_fields(data, allowed, "media_inventory", errors)
    _required_fields(data, allowed, "media_inventory", errors)
    if data.get("schema_version") != 1:
        _add_once(errors, "unsupported_media_inventory_schema_version")
    assets = data.get("assets")
    if not isinstance(assets, list):
        _add_once(errors, "invalid_media_inventory_assets")
        return {}
    inventory: dict[str, tuple[str, frozenset[str]]] = {}
    asset_fields = frozenset({"id", "factual_meaning", "immutable_facts", "role", "source"})
    required_asset_fields = frozenset({"id", "factual_meaning", "immutable_facts"})
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            _add_once(errors, f"invalid_media_inventory_asset: {index}")
            continue
        _unexpected_fields(asset, asset_fields, "media_inventory_asset", errors)
        _required_fields(asset, required_asset_fields, "media_inventory_asset", errors)
        asset_id = _text(asset.get("id"))
        meaning = _text(asset.get("factual_meaning"))
        facts = _text_list(asset.get("immutable_facts"), minimum=1)
        if asset_id is None or meaning is None or facts is None:
            _add_once(errors, f"invalid_media_inventory_asset: {index}")
            continue
        if asset_id in inventory:
            _add_once(errors, f"duplicate_media_inventory_id: {asset_id}")
        inventory[asset_id] = (meaning, frozenset(facts))
    return inventory


def _validate_energy(items: list[object], errors: list[str]) -> None:
    fields = frozenset({"section_id", "intensity", "reason"})
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            _add_once(errors, f"invalid_energy_beat: {index}")
            continue
        _unexpected_fields(item, fields, "energy_beat", errors)
        _required_fields(item, fields, "energy_beat", errors)
        label = _text(item.get("section_id")) or str(index)
        if _text(item.get("section_id")) is None:
            _add_once(errors, f"invalid_energy_section_id: {index}")
        if item.get("intensity") not in {"quiet", "rising", "peak", "release"}:
            _add_once(errors, f"invalid_energy_intensity: {label}")
        if _text(item.get("reason")) is None:
            _add_once(errors, f"invalid_energy_reason: {label}")


def _validate_images(
    items: list[object], inventory: dict[str, tuple[str, frozenset[str]]], errors: list[str]
) -> set[str]:
    fields = frozenset({"image_id", "image_role", "factual_meaning", "immutable_facts"})
    analyzed: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            _add_once(errors, f"invalid_image_analysis: {index}")
            continue
        _unexpected_fields(item, fields, "image_analysis", errors)
        _required_fields(item, fields, "image_analysis", errors)
        image_id = _text(item.get("image_id"))
        if image_id is None:
            _add_once(errors, f"invalid_image_id: {index}")
            continue
        if image_id in analyzed:
            _add_once(errors, f"duplicate_image_id: {image_id}")
        analyzed.add(image_id)
        if _text(item.get("image_role")) is None:
            _add_once(errors, f"missing_image_role: {image_id}")
        meaning = _text(item.get("factual_meaning"))
        if meaning is None:
            _add_once(errors, f"missing_factual_meaning: {image_id}")
        facts = _text_list(item.get("immutable_facts"), minimum=1)
        if facts is None:
            _add_once(errors, f"missing_immutable_facts: {image_id}")
        trusted = inventory.get(image_id)
        if trusted is None:
            _add_once(errors, f"unauthorized_media_id: {image_id}")
        else:
            trusted_meaning, trusted_facts = trusted
            if meaning is not None and meaning != trusted_meaning:
                _add_once(errors, f"factual_meaning_mismatch: {image_id}")
            if facts is not None and frozenset(facts) != trusted_facts:
                _add_once(errors, f"immutable_facts_mismatch: {image_id}")
    return analyzed


def _validate_directions(items: list[object], errors: list[str]) -> set[str]:
    fields = frozenset({"id", "name", "summary", "comparison"})
    comparison_fields = frozenset(COMPARISON_FIELDS)
    direction_ids: set[str] = set()
    if len(items) < 2:
        _add_once(errors, "insufficient_internal_directions")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            _add_once(errors, f"invalid_internal_direction: {index}")
            continue
        _unexpected_fields(item, fields, "internal_direction", errors)
        _required_fields(item, fields, "internal_direction", errors)
        direction_id = _text(item.get("id"))
        if direction_id is None:
            _add_once(errors, f"invalid_internal_direction: {index}")
            continue
        if direction_id in direction_ids:
            _add_once(errors, f"duplicate_internal_direction: {direction_id}")
        direction_ids.add(direction_id)
        if _text(item.get("name")) is None or _text(item.get("summary")) is None:
            _add_once(errors, f"invalid_internal_direction: {direction_id}")
        comparison = item.get("comparison")
        if not isinstance(comparison, dict):
            _add_once(errors, f"invalid_direction_comparison: {direction_id}")
            continue
        _unexpected_fields(comparison, comparison_fields, "direction_comparison", errors)
        _required_fields(comparison, comparison_fields, "direction_comparison", errors)
        if any(_text(comparison.get(field)) is None for field in COMPARISON_FIELDS):
            _add_once(errors, f"invalid_direction_comparison: {direction_id}")
    return direction_ids


def _validate_controller(controller: object, label: str, errors: list[str]) -> dict[str, object] | None:
    fields = frozenset({"id", "type", "targets", "properties", "handoff", "conflict_resolution"})
    if not isinstance(controller, dict):
        _add_once(errors, f"invalid_controller: {label}")
        return None
    _unexpected_fields(controller, fields, "controller", errors)
    _required_fields(controller, fields, "controller", errors)
    controller_id = _text(controller.get("id")) or label
    if _text(controller.get("id")) is None:
        _add_once(errors, f"missing_controller_id: {label}")
    if controller.get("type") not in CONTROLLER_TYPES:
        _add_once(errors, f"invalid_controller_type: {controller_id}")
    if _text_list(controller.get("targets"), minimum=1) is None:
        _add_once(errors, f"invalid_controller_targets: {controller_id}")
    if _text_list(controller.get("properties"), minimum=1) is None:
        _add_once(errors, f"invalid_controller_properties: {controller_id}")
    if _text(controller.get("handoff")) is None:
        _add_once(errors, f"missing_controller_handoff: {controller_id}")
    if _text(controller.get("conflict_resolution")) is None:
        _add_once(errors, f"missing_controller_conflict_resolution: {controller_id}")
    return controller


def _validate_sections(
    items: list[object], inventory: dict[str, tuple[str, frozenset[str]]], errors: list[str]
) -> list[dict[str, object]]:
    fields = frozenset({"section_id", "image_ids", "composition", "effects", "purpose", "controllers", "mobile", "reduced_motion"})
    controllers: list[dict[str, object]] = []
    if not items:
        _add_once(errors, "missing_section_directions")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            _add_once(errors, f"invalid_section_direction: {index}")
            continue
        _unexpected_fields(item, fields, "section_direction", errors)
        _required_fields(item, fields, "section_direction", errors)
        section_id = _text(item.get("section_id")) or str(index)
        if _text(item.get("section_id")) is None:
            _add_once(errors, f"invalid_section_id: {index}")
        image_ids = _text_list(item.get("image_ids"))
        if image_ids is None:
            _add_once(errors, f"invalid_section_image_ids: {section_id}")
        else:
            for image_id in image_ids:
                if image_id not in inventory:
                    _add_once(errors, f"unauthorized_media_id: {image_id}")
        for field in ("composition", "purpose", "mobile", "reduced_motion"):
            if _text(item.get(field)) is None:
                _add_once(errors, f"missing_section_{field}: {section_id}")
        if _text_list(item.get("effects")) is None:
            _add_once(errors, f"invalid_section_effects: {section_id}")
        raw_controllers = item.get("controllers")
        if not isinstance(raw_controllers, list):
            _add_once(errors, f"invalid_section_controllers: {section_id}")
        else:
            for controller_index, controller in enumerate(raw_controllers):
                validated = _validate_controller(controller, f"{section_id}:{controller_index}", errors)
                if validated is not None:
                    controllers.append(validated)
    return controllers


def _validate_controller_ownership(controllers: list[dict[str, object]], errors: list[str]) -> None:
    owners: dict[tuple[str, str], list[dict[str, object]]] = {}
    for controller in controllers:
        targets = _text_list(controller.get("targets"), minimum=1)
        properties = _text_list(controller.get("properties"), minimum=1)
        if targets is None or properties is None:
            continue
        for target in targets:
            for property_name in properties:
                owners.setdefault((target, property_name), []).append(controller)
    for (target, property_name), claimed_by in owners.items():
        if len(claimed_by) < 2:
            continue
        if not all(_text(owner.get("handoff")) and _text(owner.get("conflict_resolution")) for owner in claimed_by):
            _add_once(errors, f"controller_conflict_unresolved: {target}.{property_name}")


def _validate_compatibility(items: list[object], errors: list[str]) -> None:
    fields = frozenset({"controller", "owners", "resolution"})
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            _add_once(errors, f"invalid_interaction_compatibility: {index}")
            continue
        _unexpected_fields(item, fields, "interaction_compatibility", errors)
        _required_fields(item, fields, "interaction_compatibility", errors)
        label = _text(item.get("controller")) or str(index)
        if _text(item.get("controller")) is None:
            _add_once(errors, f"invalid_interaction_controller: {index}")
        owners = _text_list(item.get("owners"), minimum=1)
        if owners is None:
            _add_once(errors, f"invalid_interaction_owners: {label}")
        if _text(item.get("resolution")) is None:
            _add_once(errors, f"interaction_conflict_unresolved: {label}")


def validate_media_art_direction(
    path: Path, media_inventory_path: Path | None
) -> MediaDirectionValidationReport:
    errors: list[str] = []
    payload = _read_json(path, "report", errors)
    if not isinstance(payload, dict):
        if payload is not None:
            _add_once(errors, "report_must_be_object")
        return MediaDirectionValidationReport(False, tuple(errors))
    _unexpected_fields(payload, REPORT_FIELDS, "report", errors)
    _required_fields(payload, REPORT_FIELDS, "report", errors)
    if payload.get("schema_version") != 1:
        _add_once(errors, "unsupported_schema_version")
    for field in TEXT_REPORT_FIELDS:
        if _text(payload.get(field)) is None:
            _add_once(errors, f"invalid_{field}")
    _structured_text_object(
        payload.get("design_read"),
        frozenset({"page_kind", "audience", "vibe"}),
        "design_read",
        errors,
    )
    _structured_text_object(
        payload.get("responsive_strategy"),
        frozenset({"desktop", "tablet", "mobile", "coarse_pointer"}),
        "responsive_strategy",
        errors,
    )
    _structured_text_object(
        payload.get("reduced_motion_strategy"),
        frozenset({"trigger", "replacement", "content_visibility"}),
        "reduced_motion_strategy",
        errors,
    )
    for field in LIST_REPORT_FIELDS:
        if not isinstance(payload.get(field), list):
            _add_once(errors, f"invalid_{field}")

    image_items = payload.get("image_analysis")
    section_items = payload.get("section_directions")
    inventory: dict[str, tuple[str, frozenset[str]]] = {}
    if media_inventory_path is None:
        _add_once(errors, "authorized_media_inventory_required")
    else:
        inventory = _load_inventory(media_inventory_path, errors)

    if isinstance(image_items, list):
        if inventory and not image_items:
            _add_once(errors, "missing_image_analysis")
        _validate_images(image_items, inventory, errors)
    if isinstance(payload.get("energy_curve"), list):
        _validate_energy(payload["energy_curve"], errors)
        if not payload["energy_curve"]:
            _add_once(errors, "missing_energy_curve")
    direction_ids = _validate_directions(payload["internal_directions"], errors) if isinstance(payload.get("internal_directions"), list) else set()
    selected = _text(payload.get("selected_direction_id"))
    if selected is not None and selected not in direction_ids:
        _add_once(errors, "selected_direction_missing")
    controllers = _validate_sections(section_items, inventory, errors) if isinstance(section_items, list) else []
    _validate_controller_ownership(controllers, errors)
    if isinstance(payload.get("interaction_compatibility"), list):
        _validate_compatibility(payload["interaction_compatibility"], errors)
    for field in ("media_upgrades", "implementation_choices", "preserve"):
        items = payload.get(field)
        minimum = 1 if field in {"implementation_choices", "preserve"} else 0
        if isinstance(items, list) and _text_list(items, minimum=minimum) is None:
            _add_once(errors, f"invalid_{field}")
    return MediaDirectionValidationReport(not errors, tuple(errors))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a media art direction report.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--media-inventory", type=Path, required=True)
    args = parser.parse_args(argv)
    report = validate_media_art_direction(args.report, args.media_inventory)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
