"""Shared validation for explicit quick-mode design and execution approval."""
from __future__ import annotations

import hashlib
import re
from typing import Any

DESIGN_CATEGORIES = ("typography", "color", "media", "primary_motion", "secondary_motion")
TODO_PATH = ".resume-site-work/reports/site-todo-plan.md"


def interaction_mode(payload: Any) -> str:
    # Existing workspaces keep their original detailed review flow.
    return payload.get("interaction_mode", "deep") if isinstance(payload, dict) else "deep"


def validate_bundle(spec: dict[str, Any]) -> list[str]:
    bundle = spec.get("bundle_approval")
    if not isinstance(bundle, dict):
        return ["quick mode requires bundle_approval"]
    errors = []
    for field in ("id", "quote"):
        if not isinstance(bundle.get(field), str) or not bundle[field].strip():
            errors.append(f"bundle approval requires {field}")
    if (bundle.get("status"), bundle.get("source"), bundle.get("channel")) != (
        "user_approved", "explicit_user", "conversation"
    ):
        errors.append("bundle approval must be explicit and conversational")
    if bundle.get("structure_delegated") is not True:
        errors.append("bundle must approve structure delegation")
    if bundle.get("execution_delegated") is not True:
        errors.append("bundle must approve execution delegation")
    if bundle.get("todo_plan") != TODO_PATH:
        errors.append("bundle must identify the displayed TODO plan")
    if not isinstance(bundle.get("todo_plan_sha256"), str) or not re.fullmatch(
        r"[0-9a-f]{64}", bundle["todo_plan_sha256"]
    ):
        errors.append("bundle requires a SHA-256 of the displayed TODO plan")
    selections = bundle.get("selected_candidate_ids")
    if not isinstance(selections, dict) or set(selections) != set(DESIGN_CATEGORIES):
        errors.append("bundle must bind all five category selections")
        selections = {}
    decisions = spec.get("decisions", {})
    if not isinstance(decisions, dict):
        return errors + ["bundle decisions must be an object"]
    previews = set()
    for category in ("structure", *DESIGN_CATEGORIES):
        decision = decisions.get(category, {})
        if not isinstance(decision, dict):
            continue
        approval = decision.get("approval", {})
        if not isinstance(approval, dict) or approval.get("bundle_id") != bundle.get("id"):
            errors.append(f"{category} approval must reference the current bundle")
        if category != "structure":
            expected = [] if decision.get("status") == "skipped" else decision.get("selected_candidate_ids")
            if selections.get(category) != expected:
                errors.append(f"{category} selection differs from the approved bundle")
        preview = decision.get("preview", {})
        if isinstance(preview, dict) and preview.get("response") == "accepted":
            if isinstance(preview.get("artifact"), str):
                previews.add(preview["artifact"])
            else:
                errors.append(f"{category} preview artifact must be a string")
    if len(previews) > 1:
        errors.append("quick mode must reuse one preview gallery")
    approval = spec.get("requirements_approval", {})
    if not isinstance(approval, dict) or approval.get("bundle_id") != bundle.get("id"):
        errors.append("requirements approval must reference the current bundle")
    return errors


def validate_quick_plan(plan: dict, spec: Any, todo_bytes: bytes | None) -> list[str]:
    if not isinstance(spec, dict):
        return ["quick plan requires its approved design spec"]
    errors = validate_bundle(spec)
    if interaction_mode(spec) != "quick" or plan.get("design_spec_id") != spec.get("spec_id"):
        errors.append("quick plan must reference the matching quick design spec")
    bundle = spec.get("bundle_approval")
    if not isinstance(bundle, dict):
        return errors
    if plan.get("bundle_approval_id") != bundle.get("id"):
        errors.append("plan must reference the current approved bundle")
    approval = plan.get("todo_plan_approval", {})
    if not isinstance(approval, dict) or approval.get("bundle_id") != bundle.get("id"):
        errors.append("TODO approval must reference the current approved bundle")
    if todo_bytes is None:
        errors.append("quick plan requires the displayed TODO file")
    elif hashlib.sha256(todo_bytes).hexdigest() != bundle.get("todo_plan_sha256"):
        errors.append("TODO plan changed after bundle approval")
    return errors
