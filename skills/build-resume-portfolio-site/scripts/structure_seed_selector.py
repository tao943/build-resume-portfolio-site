from __future__ import annotations

import argparse
import json
import random
import uuid
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


SIGNATURE_FIELDS = ("axis", "anchor", "evidence_transition", "viewport_relationship", "mobile_transform")
SIGNATURE_WEIGHTS = {"axis": 0.25, "anchor": 0.20, "evidence_transition": 0.20, "viewport_relationship": 0.20, "mobile_transform": 0.15}
FINGERPRINT_WEIGHTS = {
    "structure_origin": 0.12, "structure_seed": 0.18, "reading_axis": 0.14,
    "hero_gravity": 0.12, "visual_protagonist": 0.14, "project_pattern": 0.12,
    "motion_family": 0.08, "surface_language": 0.06, "color_strategy": 0.04,
}
REQUIRED_FINGERPRINT_FIELDS = {"generation_id", "structure_origin", "reading_axis", "hero_gravity", "visual_protagonist", "project_pattern", "color_strategy", "motion_family", "surface_language"}


def _items(value: object) -> Sequence[object]:
    return value if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) else ()


def build_structural_profile(content_map: Mapping[str, object], media_inventory: Mapping[str, object], constraints: Mapping[str, object]) -> dict[str, object]:
    projects = _items(content_map.get("projects"))
    experience = _items(content_map.get("experience")) or _items(content_map.get("experiences"))
    skills = _items(content_map.get("skills"))
    media = content_map.get("media") if isinstance(content_map.get("media"), Mapping) else {}
    merged_media = {**media, **media_inventory}
    media_count = sum(int(v) if isinstance(v, int) and not isinstance(v, bool) else int(v is True) for v in merged_media.values())
    density_score = len(projects) * 2 + len(experience) * 2 + len(skills)
    return {
        "project_count": len(projects),
        "experience_count": len(experience),
        "skill_count": len(skills),
        "copy_density": "high" if density_score >= 14 else "medium" if density_score >= 5 else "low",
        "media_profile": "rich" if media_count >= 4 else "limited" if media_count else "none",
        "max_layout_cost": int(constraints.get("max_layout_cost", 3)),
        "max_motion_cost": int(constraints.get("max_motion_cost", 3)),
        "allow_three_d": bool(constraints.get("allow_three_d", False)),
    }


def filter_feasible_seeds(catalog: Mapping[str, object], profile: Mapping[str, object]) -> dict[str, list[dict[str, object]]]:
    accepted: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    for raw in _items(catalog.get("seeds")):
        seed = dict(raw) if isinstance(raw, Mapping) else {}
        reasons: list[str] = []
        capacity = seed.get("capacity") if isinstance(seed.get("capacity"), Mapping) else {}
        projects = capacity.get("projects") if isinstance(capacity.get("projects"), Mapping) else {}
        if int(profile.get("project_count", 0)) < int(projects.get("min", 0)):
            reasons.append("insufficient_projects")
        if profile.get("media_profile") not in _items(capacity.get("media")):
            reasons.append("media_profile_unsupported")
        if profile.get("copy_density") not in _items(capacity.get("copy_density")):
            reasons.append("copy_density_unsupported")
        cost = seed.get("cost") if isinstance(seed.get("cost"), Mapping) else {}
        if int(cost.get("layout", 0)) > int(profile.get("max_layout_cost", 3)):
            reasons.append("layout_cost_exceeds_budget")
        if int(cost.get("motion", 0)) > int(profile.get("max_motion_cost", 3)):
            reasons.append("motion_cost_exceeds_budget")
        # 3D is always optional in seeds, so disabling it never rejects topology.
        if reasons:
            rejected.append({"id": seed.get("id", "unknown"), "reason_codes": reasons})
        else:
            accepted.append(seed)
    return {"accepted": accepted, "rejected": rejected}


def canonical_topology_signature(value: Mapping[str, object]) -> dict[str, str]:
    signature = value.get("canonical_signature") if isinstance(value.get("canonical_signature"), Mapping) else value
    return {field: str(signature.get(field, "")).strip().casefold() for field in SIGNATURE_FIELDS}


def topology_distance(left: Mapping[str, object], right: Mapping[str, object]) -> float:
    a, b = canonical_topology_signature(left), canonical_topology_signature(right)
    return round(sum(SIGNATURE_WEIGHTS[field] for field in SIGNATURE_FIELDS if a[field] != b[field]), 6)


def fingerprint_distance(left: Mapping[str, object], right: Mapping[str, object]) -> float:
    return round(sum(weight for field, weight in FINGERPRINT_WEIGHTS.items() if left.get(field) != right.get(field)), 6)


def _history_seed_penalty(seed_id: str, history: Sequence[Mapping[str, object]]) -> float:
    recent = list(history)[-3:]
    return 0.25 if any(item.get("structure_seed") == seed_id for item in recent) else 0.0


def _history_distance(seed: Mapping[str, object], history: Sequence[Mapping[str, object]]) -> float:
    if not history:
        return 1.0
    axis = canonical_topology_signature(seed)["axis"]
    values = []
    for item in history[-20:]:
        distance = 0.65 if item.get("structure_seed") != seed.get("id") else 0.0
        if item.get("reading_axis") != axis:
            distance += 0.35
        values.append(distance)
    return sum(values) / len(values)


def _quality(seed: Mapping[str, object], profile: Mapping[str, object]) -> float:
    capacity = seed["capacity"]
    projects = capacity["projects"]
    count = int(profile["project_count"])
    preferred = int(projects["preferred_max"])
    capacity_fit = 1.0 if count <= preferred else max(0.5, 1.0 - (count - preferred) * 0.08)
    cost = seed["cost"]
    survivability = 1.0 if seed.get("responsive_transformations") else 0.0
    static = 1.0 if all(slot.get("optional") is True for slot in seed.get("motion_slots", [])) else 0.0
    delivery = 1.0 - (float(cost["layout"]) + float(cost["motion"])) / 12.0
    composition = 0.85 + min(len(seed.get("invariants", [])), 3) * 0.05
    return 0.30 * capacity_fit + 0.25 * composition + 0.20 * survivability + 0.15 * static + 0.10 * delivery


def select_seed_pair(catalog: Mapping[str, object], profile: Mapping[str, object], history: Sequence[Mapping[str, object]], generation_id: str) -> dict[str, object]:
    result = filter_feasible_seeds(catalog, profile)
    candidates = result["accepted"]
    fallback_reason = None
    if len(candidates) < 2:
        fallback = next((seed for seed in catalog.get("seeds", []) if seed.get("id") == "architectural-breakout-grid"), None)
        if fallback is None:
            raise ValueError("catalog has no feasible pair or fallback")
        candidates = [fallback] + [seed for seed in catalog.get("seeds", []) if seed.get("id") != fallback["id"]][:1]
        fallback_reason = "no_feasible_seed_pair"
    rng = random.Random(str(generation_id))
    ranked = []
    for seed in candidates:
        quality = _quality(seed, profile)
        novelty = _history_distance(seed, history)
        penalty = _history_seed_penalty(str(seed["id"]), history)
        ranked.append((0.84 * quality + 0.06 * novelty + 0.10 * rng.random() - penalty, quality, novelty, seed))
    ranked.sort(key=lambda item: (item[0], item[3]["id"]), reverse=True)
    fit = ranked[0]
    novelty_pool = [item for item in ranked if item[3]["id"] != fit[3]["id"] and item[1] >= max(0.65, fit[1] - 0.15)]
    novelty_pool.sort(key=lambda item: (0.65 * item[1] + 0.30 * item[2] + 0.05 * item[0], item[3]["id"]), reverse=True)
    novelty = novelty_pool[0] if novelty_pool else ranked[1]
    return {
        "fit": {"id": fit[3]["id"], "quality": round(fit[1], 6), "history_distance": round(fit[2], 6)},
        "novelty": {"id": novelty[3]["id"], "quality": round(novelty[1], 6), "history_distance": round(novelty[2], 6)},
        "rejected": result["rejected"],
        "fallback_reason": fallback_reason,
    }


def validate_fingerprint(value: Mapping[str, object]) -> list[str]:
    errors = [f"missing fingerprint field: {field}" for field in sorted(REQUIRED_FINGERPRINT_FIELDS) if not isinstance(value.get(field), str) or not str(value[field]).strip()]
    if value.get("schema_version") != 1:
        errors.append("fingerprint schema_version must be 1")
    return errors


def load_history(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"malformed visual fingerprint history: {error}") from error
    items = value.get("items") if isinstance(value, Mapping) else None
    if not isinstance(items, list):
        raise ValueError("malformed visual fingerprint history: items must be a list")
    for item in items:
        if not isinstance(item, Mapping) or validate_fingerprint(item):
            raise ValueError("malformed visual fingerprint history: invalid item")
    return [dict(item) for item in items]


def record_successful_fingerprint(path: Path, fingerprint: Mapping[str, object], audit_passed: bool) -> None:
    if not audit_passed:
        return
    errors = validate_fingerprint(fingerprint)
    if errors:
        raise ValueError("; ".join(errors))
    try:
        history = load_history(path)
    except ValueError:
        quarantine = path.with_name(f"{path.name}.corrupt-{uuid.uuid4().hex}")
        path.replace(quarantine)
        raise
    generation_id = fingerprint["generation_id"]
    history = [item for item in history if item.get("generation_id") != generation_id]
    history.append(dict(fingerprint))
    value = {"schema_version": 1, "items": history[-20:]}
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def audit_allows_history(audit: Mapping[str, object]) -> bool:
    if audit.get("overall_status") != "pass":
        return False
    review = audit.get("structure_review")
    if audit.get("schema_version") == 2:
        if not isinstance(review, Mapping):
            return False
        return all(review.get(field) == "pass" for field in ("seed_identity", "visual_protagonist", "mobile_transformation", "static_without_motion", "novelty_not_palette_only"))
    return True


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage structure-seed visual history.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("--history", required=True, type=Path)
    record_parser.add_argument("--fingerprint", required=True, type=Path)
    record_parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        fingerprint = json.loads(args.fingerprint.read_text(encoding="utf-8"))
        audit = json.loads(args.audit.read_text(encoding="utf-8"))
        if not isinstance(fingerprint, Mapping) or not isinstance(audit, Mapping):
            raise ValueError("fingerprint and audit must be JSON objects")
        passed = audit_allows_history(audit)
        record_successful_fingerprint(args.history, fingerprint, audit_passed=passed)
        if not passed:
            print("ERROR: final visual audit does not permit history write")
            return 1
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1
    print("OK: visual fingerprint history updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
