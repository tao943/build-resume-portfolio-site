from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_NODE_IDS = [
    "start",
    "extract_facts",
    "validate_facts",
    "clarification_decision",
    "clarification_question",
    "jd_match",
    "content_strategies",
    "strategy_approval",
    "tailored_copy",
    "copy_approval",
    "content_map",
    "creative_directions",
    "direction_approval",
    "generate_preview_html",
    "preview_delivery",
    "preview_review",
]
REQUIRED_STATE = {
    "source_facts",
    "confirmed_facts",
    "clarification_queue",
    "jd_match_matrix",
    "approved_copy",
    "content_map",
    "creative_direction",
    "preview_artifact",
}
FORBIDDEN_CAPABILITIES = {"model_inference", "copy_rewrite", "fact_invention"}


def validate(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["workflow spec must be an object"]

    errors: list[str] = []
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if payload.get("platform") != "iflytek-astron-agent":
        errors.append("platform must be iflytek-astron-agent")
    if payload.get("entry_kind") != "workflow-agent":
        errors.append("entry_kind must be workflow-agent")

    nodes = payload.get("nodes", [])
    if not isinstance(nodes, list):
        nodes = []
    node_ids = [node.get("id") for node in nodes if isinstance(node, dict)]
    if node_ids != REQUIRED_NODE_IDS:
        errors.append("workflow nodes are missing or out of order")

    approvals = [
        node.get("approval_kind")
        for node in nodes
        if isinstance(node, dict) and node.get("approval_kind")
    ]
    if approvals != ["content_strategy", "final_copy", "creative_direction"]:
        errors.append("approval gates must remain separate and ordered")

    if payload.get("approval_sources") != ["explicit_conversation"]:
        errors.append("approval_sources must equal ['explicit_conversation']")

    state_variables = payload.get("state_variables", [])
    state = set(state_variables) if isinstance(state_variables, list) else set()
    if state != REQUIRED_STATE:
        errors.append("state_variables do not match the approved contract")

    capabilities = payload.get("preview_service_capabilities", [])
    if not isinstance(capabilities, list):
        capabilities = []
    for capability in capabilities:
        if capability in FORBIDDEN_CAPABILITIES:
            errors.append(f"preview service capability is forbidden: {capability}")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_workflow_spec.py <workflow-spec.json>")
        return 2
    path = Path(sys.argv[1])
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    errors = validate(payload)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("OK: Xinghuo workflow spec is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
