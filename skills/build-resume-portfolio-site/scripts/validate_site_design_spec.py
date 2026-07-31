from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any


DECISION_ORDER = (
    "structure",
    "typography",
    "color",
    "media",
    "primary_motion",
    "secondary_motion",
)
REQUIRED = {
    "schema_version",
    "spec_id",
    "workflow_mode",
    "content_revision",
    "decision_order",
    "decisions",
    "engineering_constraints",
    "requirements_approval",
}
REQUIRED_ENGINEERING_CONSTRAINTS = {
    "responsive",
    "accessible",
    "coarse-pointer",
    "reduced-motion",
    "media-fallbacks",
}
PLACEHOLDERS = {"todo", "tbd", "implement later", "fill in details"}


def _strings(value: Any, *, non_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not non_empty)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def _contains_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in PLACEHOLDERS
    if isinstance(value, list):
        return any(_contains_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_placeholder(item) for item in value.values())
    return False


def _validate_approval(approval: Any, subject: str) -> list[str]:
    verb = "require" if subject == "final requirements" else "requires"
    if not isinstance(approval, dict):
        return [f"{subject} {verb} explicit approval"]
    if approval.get("status") != "user_approved":
        return [f"{subject} {verb} user approval"]
    if (
        approval.get("source") != "explicit_user"
        or approval.get("channel") != "conversation"
    ):
        return [f"{subject} approval must be explicit and conversational"]
    return []


def _validate_preview(preview: Any, category: str) -> list[str]:
    if not isinstance(preview, dict):
        return [f"{category} requires a preview record"]
    errors: list[str] = []
    if preview.get("offered") is not True:
        errors.append(f"{category} preview must be offered")
    response = preview.get("response")
    delivery = preview.get("delivery")
    artifact = preview.get("artifact")
    if response not in {"accepted", "declined"}:
        errors.append(f"{category} preview response is invalid")
    if delivery not in {
        "local-gallery",
        "static-fallback",
        "not-requested",
    }:
        errors.append(f"{category} preview delivery is invalid")
    if response == "declined":
        if delivery != "not-requested" or artifact is not None:
            errors.append(
                f"{category} declined preview must not have an artifact"
            )
        return errors
    if delivery == "not-requested":
        errors.append(f"{category} accepted preview requires delivery")
    normalized = str(artifact or "").replace("\\", "/")
    artifact_path = PurePosixPath(normalized)
    expected_prefix = (
        ".resume-site-work",
        "style-preview",
        "sessions",
    )
    if (
        artifact_path.is_absolute()
        or ".." in artifact_path.parts
        or artifact_path.parts[:3] != expected_prefix
        or len(artifact_path.parts) != 5
        or artifact_path.parts[-1] != "gallery.html"
    ):
        errors.append(
            f"{category} preview artifact must be a session gallery"
        )
    return errors


def _validate_candidates(candidates: Any, category: str) -> tuple[list[str], list[str]]:
    if not isinstance(candidates, list) or len(candidates) < 2:
        return [], [f"{category} requires at least two candidates"]
    errors: list[str] = []
    ids: list[str] = []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"{category} candidate[{index}] must be an object")
            continue
        candidate_id = candidate.get("id")
        label = candidate.get("label")
        tradeoffs = candidate.get("tradeoffs")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            errors.append(f"{category} candidate[{index}] requires an ID")
            continue
        ids.append(candidate_id)
        if not isinstance(label, str) or not label.strip():
            errors.append(f"{category} candidate[{index}] requires a label")
        if not _strings(tradeoffs, non_empty=True):
            errors.append(
                f"{category} candidate[{index}] requires tradeoffs"
            )
    if len(ids) != len(set(ids)):
        errors.append(f"{category} candidate IDs must be unique")
    return ids, errors


def _validate_confirmed_decision(
    category: str,
    decision: Any,
    *,
    allow_multiple: bool,
) -> list[str]:
    if not isinstance(decision, dict) or decision.get("status") != "confirmed":
        return [f"{category} must be confirmed"]
    candidate_ids, errors = _validate_candidates(
        decision.get("candidates"), category
    )
    known = set(candidate_ids)
    if decision.get("recommended_candidate_id") not in known:
        errors.append(f"{category} recommendation must reference a candidate")
    for field in ("tentative_selection_ids", "selected_candidate_ids"):
        selected = decision.get(field)
        if not _strings(selected, non_empty=True):
            errors.append(f"{category} {field} must be non-empty")
            continue
        if len(selected) != len(set(selected)):
            errors.append(f"{category} {field} must be unique")
        if not allow_multiple and len(selected) != 1:
            errors.append(
                f"{category} requires exactly one selected candidate"
            )
        if not set(selected) <= known:
            errors.append(f"{category} {field} must reference candidates")
    errors.extend(_validate_preview(decision.get("preview"), category))
    errors.extend(_validate_approval(decision.get("approval"), category))
    return errors


def _validate_media_decision(decision: Any) -> list[str]:
    if isinstance(decision, dict) and decision.get("status") == "skipped":
        reason = decision.get("skip_reason")
        if not isinstance(reason, str) or not reason.strip():
            return ["media skip requires a reason"]
        return []
    return _validate_confirmed_decision(
        "media", decision, allow_multiple=False
    )


def validate(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["site design spec must be a JSON object"]
    errors = [
        f"missing field: {name}"
        for name in sorted(REQUIRED - set(payload))
    ]
    if errors:
        return errors
    if payload["schema_version"] != 3:
        errors.append("schema_version must be 3")
    if payload["workflow_mode"] not in {"full", "fast-change"}:
        errors.append("workflow_mode must be full or fast-change")
    if (
        not isinstance(payload["spec_id"], str)
        or not payload["spec_id"].strip()
    ):
        errors.append("spec_id must be a non-empty string")
    if (
        not isinstance(payload["content_revision"], int)
        or isinstance(payload["content_revision"], bool)
        or payload["content_revision"] < 1
    ):
        errors.append("content_revision must be a positive integer")
    if tuple(payload["decision_order"]) != DECISION_ORDER:
        errors.append("decision_order must match the required workflow order")

    decisions = payload["decisions"]
    if not isinstance(decisions, dict):
        errors.append("decisions must be an object")
    else:
        missing = set(DECISION_ORDER) - set(decisions)
        for category in sorted(missing):
            errors.append(f"decisions missing category: {category}")
        for category in ("structure", "typography", "color"):
            if category in decisions:
                errors.extend(
                    _validate_confirmed_decision(
                        category,
                        decisions[category],
                        allow_multiple=False,
                    )
                )
        if "media" in decisions:
            errors.extend(_validate_media_decision(decisions["media"]))
        if "primary_motion" in decisions:
            errors.extend(
                _validate_confirmed_decision(
                    "primary_motion",
                    decisions["primary_motion"],
                    allow_multiple=False,
                )
            )
        if "secondary_motion" in decisions:
            errors.extend(
                _validate_confirmed_decision(
                    "secondary_motion",
                    decisions["secondary_motion"],
                    allow_multiple=True,
                )
            )

    constraints = payload["engineering_constraints"]
    if not _strings(constraints, non_empty=True):
        errors.append("engineering_constraints must be a non-empty string list")
    elif not REQUIRED_ENGINEERING_CONSTRAINTS <= set(constraints):
        errors.append("engineering_constraints omit mandatory constraints")
    errors.extend(
        _validate_approval(
            payload["requirements_approval"], "final requirements"
        )
    )
    if _contains_placeholder(payload):
        errors.append("placeholder text is not allowed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a website discovery design specification."
    )
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.spec.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read site design spec: {exc}")
        return 1
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: site design spec is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
