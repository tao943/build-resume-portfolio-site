from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


SIGNATURE_FIELDS = ("axis", "anchor", "evidence_transition", "viewport_relationship", "mobile_transform")
REQUIRED_FIELDS = (
    "id", "label", "reading_path", "topology", "canonical_signature", "capacity",
    "invariants", "variation_axes", "motion_slots", "responsive_transformations",
    "anti_degeneracy_rules", "cost", "tags",
)
FORBIDDEN_KEYS = {"jsx", "html", "palette", "colors", "font", "fonts", "component", "components", "asset", "assets", "shader", "duration", "easing"}


def _non_empty_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _walk_keys(value: object) -> list[str]:
    if isinstance(value, Mapping):
        return [str(key).casefold() for key in value] + [key for child in value.values() for key in _walk_keys(child)]
    if isinstance(value, list):
        return [key for child in value for key in _walk_keys(child)]
    return []


def validate_catalog(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, Mapping):
        return ["catalog must be an object"]
    if value.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(value.get("catalog_version"), str) or not re.fullmatch(r"\d+\.\d+\.\d+", value["catalog_version"]):
        errors.append("catalog_version must be semantic version")
    seeds = value.get("seeds")
    if not isinstance(seeds, list) or not 8 <= len(seeds) <= 12:
        return errors + ["seeds must contain 8..12 items"]
    seen: set[str] = set()
    for index, seed in enumerate(seeds):
        prefix = f"seeds[{index}]"
        if not isinstance(seed, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        missing = [field for field in REQUIRED_FIELDS if field not in seed]
        errors.extend(f"{prefix}.{field} is required" for field in missing)
        seed_id = seed.get("id")
        if not isinstance(seed_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", seed_id):
            errors.append(f"{prefix}.id must be kebab-case")
        elif seed_id in seen:
            errors.append(f"duplicate seed id: {seed_id}")
        else:
            seen.add(seed_id)
        forbidden = sorted(FORBIDDEN_KEYS.intersection(_walk_keys(seed)))
        if forbidden:
            errors.append(f"{prefix} contains forbidden template keys: {', '.join(forbidden)}")
        signature = seed.get("canonical_signature")
        if not isinstance(signature, Mapping) or set(signature) != set(SIGNATURE_FIELDS) or not all(isinstance(signature.get(k), str) and signature[k] for k in SIGNATURE_FIELDS):
            errors.append(f"{prefix}.canonical_signature must contain the five canonical fields")
        for field in ("invariants", "variation_axes", "responsive_transformations", "anti_degeneracy_rules", "tags"):
            if not _non_empty_list(seed.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string list")
        slots = seed.get("motion_slots")
        if not isinstance(slots, list) or not slots:
            errors.append(f"{prefix}.motion_slots must be non-empty")
        else:
            for slot_index, slot in enumerate(slots):
                if not isinstance(slot, Mapping) or slot.get("optional") is not True or not _non_empty_list(slot.get("families")):
                    errors.append(f"{prefix}.motion_slots[{slot_index}] must be optional with families")
        cost = seed.get("cost")
        if not isinstance(cost, Mapping):
            errors.append(f"{prefix}.cost must be an object")
        else:
            for key in ("layout", "motion", "three_d"):
                if not isinstance(cost.get(key), int) or not 0 <= cost[key] <= 3:
                    errors.append(f"{prefix}.cost.{key} must be an integer in 0..3")
    return errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the high-impact structure seed catalog.")
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args(argv)
    try:
        value = json.loads(args.catalog.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 1
    errors = validate_catalog(value)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {len(value['seeds'])} structure seeds are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
