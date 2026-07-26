from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT_FIELDS = {
    "schema_version",
    "creative_thesis",
    "experience_priority",
    "creative_freedom",
    "layout_candidates",
    "selected_candidate_id",
    "selection_rationale",
    "concept_prototype",
    "responsive_freedom",
    "motion_freedom",
    "review_questions",
}
OPEN_FIELDS = {
    "composition",
    "layout_patterns",
    "motion_language",
    "visual_metaphor",
    "surface_treatment",
}
FORBIDDEN_KEYS = {
    "jsx",
    "html",
    "component_tree",
    "component-tree",
    "source_code",
    "source-code",
}
IMPLEMENTATION_PATTERN = re.compile(
    r"</?[a-zA-Z][^>]*>|(?:^|\s)import\s+.+\s+from\s+|"
    r"(?:^|\s)function\s+\w+\s*\(|=>\s*[{(]"
)
PIXEL_PATTERN = re.compile(r"\b\d+(?:\.\d+)?(?:px|rem|vw|vh)\b", re.IGNORECASE)
CONCEPT_FIELDS = {
    "visual_protagonist",
    "composition_commitment",
    "type_color_character",
    "representative_interaction_state",
    "template_independence_test",
    "deferred_to_later",
}
FIRST_VERSION_COMMITMENTS = (
    "selected layout",
    "layout family",
    "initial visual hierarchy",
    "initial type",
    "initial color",
    "representative interaction",
    "visual protagonist",
    "选定版式",
    "版式家族",
    "初始视觉层级",
    "初始字体",
    "初始配色",
    "代表性交互",
    "视觉主角",
)


def _string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any, minimum: int = 1) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= minimum
        and all(_string(item) for item in value)
        and len({item.strip().casefold() for item in value}) == len(value)
    )


def _normalise(value: str) -> str:
    return " ".join(value.split()).casefold().rstrip(".。")


def _walk(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    items = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            items.extend(_walk(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_walk(child, f"{path}[{index}]"))
    return items


def validate(report: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(report, dict):
        return ["report must be a JSON object"]

    missing = ROOT_FIELDS - set(report)
    if missing:
        return ["missing root fields: " + ", ".join(sorted(missing))]
    if report["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if not _string(report["creative_thesis"]):
        errors.append("creative_thesis must be a non-empty string")
    if not _string_list(report["experience_priority"], minimum=2):
        errors.append("experience_priority needs at least two unique entries")
    if not _string(report["selection_rationale"]):
        errors.append("selection_rationale must be a non-empty string")
    if not _string_list(report["review_questions"], minimum=3):
        errors.append("review_questions needs at least three unique entries")

    freedom = report["creative_freedom"]
    fixed: list[str] = []
    avoid: list[str] = []
    open_values: list[str] = []
    if not isinstance(freedom, dict) or set(freedom) != {"fixed", "open", "avoid"}:
        errors.append("creative_freedom must contain fixed, open, and avoid")
    else:
        if not _string_list(freedom["fixed"]):
            errors.append("creative_freedom.fixed must be a non-empty unique list")
        else:
            fixed = freedom["fixed"]
        if not _string_list(freedom["avoid"]):
            errors.append("creative_freedom.avoid must be a non-empty unique list")
        else:
            avoid = freedom["avoid"]
        open_space = freedom["open"]
        if not isinstance(open_space, dict) or set(open_space) != OPEN_FIELDS:
            errors.append(
                "creative_freedom.open must contain composition, layout_patterns, "
                "motion_language, visual_metaphor, and surface_treatment"
            )
        else:
            for key in sorted(OPEN_FIELDS):
                values = open_space[key]
                if not _string_list(values):
                    errors.append(f"creative_freedom.open.{key} must be non-empty")
                else:
                    open_values.extend(values)
                    for value in values:
                        if PIXEL_PATTERN.search(value):
                            errors.append(
                                f"pixel-level prescription is not allowed in open space: {key}"
                            )

    groups = {
        "fixed": {_normalise(item) for item in fixed},
        "open": {_normalise(item) for item in open_values},
        "avoid": {_normalise(item) for item in avoid},
    }
    for left, right in (("fixed", "open"), ("fixed", "avoid"), ("open", "avoid")):
        overlap = groups[left] & groups[right]
        if overlap:
            errors.append(
                f"freedom overlap between {left} and {right}: "
                + ", ".join(sorted(overlap))
            )

    candidates = report["layout_candidates"]
    candidate_ids: set[str] = set()
    families: set[str] = set()
    if not isinstance(candidates, list) or not 2 <= len(candidates) <= 3:
        errors.append("layout_candidates must contain two or three candidates")
    else:
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                errors.append(f"layout_candidates[{index}] must be an object")
                continue
            required = {"id", "family", "fit", "risks", "responsive_fallback"}
            if set(candidate) != required:
                errors.append(
                    f"layout_candidates[{index}] must contain exactly "
                    "id, family, fit, risks, and responsive_fallback"
                )
                continue
            if not all(
                _string(candidate[field])
                for field in ("id", "family", "fit", "responsive_fallback")
            ) or not _string_list(candidate["risks"]):
                errors.append(f"layout_candidates[{index}] has invalid content")
                continue
            candidate_id = candidate["id"].strip()
            family = candidate["family"].strip().casefold()
            if candidate_id in candidate_ids:
                errors.append(f"duplicate layout candidate id: {candidate_id}")
            candidate_ids.add(candidate_id)
            families.add(family)
        if len(families) < 2:
            errors.append("layout_candidates need at least two distinct layout families")

    selected = report["selected_candidate_id"]
    if not _string(selected) or selected not in candidate_ids:
        errors.append("selected_candidate_id must reference an existing candidate")

    concept = report["concept_prototype"]
    if not isinstance(concept, dict) or set(concept) != CONCEPT_FIELDS:
        errors.append(
            "concept_prototype must contain visual_protagonist, "
            "composition_commitment, type_color_character, "
            "representative_interaction_state, template_independence_test, "
            "and deferred_to_later"
        )
    else:
        for field in CONCEPT_FIELDS - {"deferred_to_later"}:
            if not _string(concept[field]):
                errors.append(f"concept_prototype.{field} must be non-empty")
        deferred = concept["deferred_to_later"]
        if not _string_list(deferred):
            errors.append("concept_prototype.deferred_to_later must be non-empty")
        else:
            for item in deferred:
                lowered = item.casefold()
                if any(marker in lowered for marker in FIRST_VERSION_COMMITMENTS):
                    errors.append(
                        "concept_prototype cannot defer first-version visual commitments"
                    )
                    break

    responsive = report["responsive_freedom"]
    if (
        not isinstance(responsive, dict)
        or set(responsive) != {"must_preserve", "may_adapt"}
        or not _string_list(responsive.get("must_preserve"))
        or not _string_list(responsive.get("may_adapt"))
    ):
        errors.append(
            "responsive_freedom needs non-empty must_preserve and may_adapt lists"
        )

    motion = report["motion_freedom"]
    if (
        not isinstance(motion, dict)
        or set(motion) != {"purpose", "allowed", "avoid"}
        or not _string(motion.get("purpose"))
        or not _string_list(motion.get("allowed"))
        or not _string_list(motion.get("avoid"))
    ):
        errors.append(
            "motion_freedom needs purpose plus non-empty allowed and avoid lists"
        )

    for path, value in _walk(report):
        key = path.rsplit(".", 1)[-1].casefold()
        if key in FORBIDDEN_KEYS:
            errors.append(f"implementation payload key is not allowed: {path}")
        if isinstance(value, str) and IMPLEMENTATION_PATTERN.search(value):
            errors.append(f"implementation payload is not allowed: {path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a portfolio creative-direction report."
    )
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.report.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: report not found: {args.report}")
        return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read report: {exc}")
        return 1

    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: creative-direction report is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
