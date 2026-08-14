from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ATS_CHECKS = (
    "completed",
    "plain_text_safe",
    "standard_headings",
    "keyword_stuffing_absent",
    "hidden_text_absent",
    "truthful_keyword_use",
)
INTEGRITY_CHECKS = (
    "ownership_supported",
    "result_supported",
    "no_invented_claims",
    "no_unmatched_jd_claims",
)


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _strings(value: object) -> bool:
    return (
        isinstance(value, list)
        and all(_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _required_fields(value: object, fields: set[str], label: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label} must be an object"]
    return [f"{label} missing field: {field}" for field in sorted(fields - set(value))]


def validate(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["content quality review must be an object"]

    errors = _required_fields(
        payload,
        {
            "schema_version",
            "review_status",
            "jd_review",
            "ats_review",
            "blocked_claims",
            "blocks",
            "copy_approval",
        },
        "report",
    )
    if errors:
        return errors
    if payload["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if payload["review_status"] != "approved":
        errors.append("review_status must be approved")

    jd_review = payload["jd_review"]
    jd_errors = _required_fields(
        jd_review,
        {"present", "matched_requirement_ids", "unmatched_requirement_ids"},
        "jd_review",
    )
    errors.extend(jd_errors)
    matched_jd: set[str] = set()
    unmatched_jd: set[str] = set()
    if not jd_errors:
        if not isinstance(jd_review["present"], bool):
            errors.append("jd_review.present must be a boolean")
        for field in ("matched_requirement_ids", "unmatched_requirement_ids"):
            if not _strings(jd_review[field]):
                errors.append(f"jd_review.{field} must be a unique string list")
        if _strings(jd_review["matched_requirement_ids"]):
            matched_jd = set(jd_review["matched_requirement_ids"])
        if _strings(jd_review["unmatched_requirement_ids"]):
            unmatched_jd = set(jd_review["unmatched_requirement_ids"])
        if matched_jd & unmatched_jd:
            errors.append("matched and unmatched JD requirement IDs must be disjoint")
        if jd_review["present"] is False and (matched_jd or unmatched_jd):
            errors.append("JD requirement IDs must be empty when no JD is present")

    ats_review = payload["ats_review"]
    ats_errors = _required_fields(ats_review, set(ATS_CHECKS) | {"notes"}, "ats_review")
    errors.extend(ats_errors)
    if not ats_errors:
        if not all(ats_review[field] is True for field in ATS_CHECKS):
            errors.append("ATS review must pass all checks")
        if not _strings(ats_review["notes"]):
            errors.append("ats_review.notes must be a unique string list")

    blocked_claims = payload["blocked_claims"]
    if not isinstance(blocked_claims, list):
        errors.append("blocked_claims must be a list")
    else:
        for index, item in enumerate(blocked_claims):
            if not isinstance(item, dict) or not all(
                _text(item.get(field)) for field in ("claim", "reason")
            ):
                errors.append(f"blocked_claims[{index}] requires claim and reason")

    blocks = payload["blocks"]
    block_ids: list[str] = []
    if not isinstance(blocks, list) or not blocks:
        errors.append("blocks must be a non-empty list")
        blocks = []
    required_block_fields = {
        "block_id",
        "source_section",
        "original_copy",
        "recommended_copy",
        "stronger_version",
        "selected_version",
        "action",
        "method",
        "scope",
        "result",
        "fact_ids",
        "evidence_ids",
        "jd_requirement_ids",
        "integrity_review",
        "approval_status",
    }
    for index, block in enumerate(blocks):
        label = f"blocks[{index}]"
        block_errors = _required_fields(block, required_block_fields, label)
        errors.extend(block_errors)
        if block_errors:
            continue
        block_id = block["block_id"]
        if not _text(block_id):
            errors.append(f"{label}.block_id must be non-empty")
        else:
            block_ids.append(block_id)
            label = block_id
        for field in ("source_section", "recommended_copy", "action", "method", "scope"):
            if not _text(block[field]):
                errors.append(f"{label}.{field} must be non-empty")
        if not isinstance(block["original_copy"], str):
            errors.append(f"{label}.original_copy must be a string")
        if not _strings(block["fact_ids"]) or not block["fact_ids"] or not _strings(
            block["evidence_ids"]
        ) or not block["evidence_ids"]:
            errors.append(f"{label} recommended copy requires fact_ids and evidence_ids")

        stronger = block["stronger_version"]
        if stronger is not None:
            if not isinstance(stronger, dict) or not _text(stronger.get("copy")):
                errors.append(f"{label}.stronger_version requires copy")
            if (
                not isinstance(stronger, dict)
                or not _strings(stronger.get("fact_ids"))
                or not stronger.get("fact_ids")
                or not _strings(stronger.get("evidence_ids"))
                or not stronger.get("evidence_ids")
            ):
                errors.append(f"{label} stronger_version requires fact_ids and evidence_ids")
        selected_version = block["selected_version"]
        if selected_version not in {"recommended", "stronger"}:
            errors.append(f"{label}.selected_version is invalid")
        elif selected_version == "stronger" and stronger is None:
            errors.append(f"{label} selected stronger version is missing")

        result = block["result"]
        result_errors = _required_fields(
            result,
            {"kind", "text", "fact_ids", "evidence_ids", "reason", "unsupported_metrics_removed"},
            f"{label}.result",
        )
        errors.extend(result_errors)
        if not result_errors:
            if not _text(result["text"]):
                errors.append(f"{label}.result.text must be non-empty")
            if not _strings(result["fact_ids"]) or not _strings(result["evidence_ids"]):
                errors.append(f"{label}.result IDs must be unique string lists")
            if result["kind"] == "evidenced":
                if not result["fact_ids"] or not result["evidence_ids"]:
                    errors.append(f"{label} evidenced result requires fact_ids and evidence_ids")
            elif result["kind"] == "qualitative_fallback":
                if not _text(result["reason"]) or result["unsupported_metrics_removed"] is not True:
                    errors.append(
                        f"{label} qualitative fallback requires a reason and removed unsupported metrics"
                    )
            else:
                errors.append(f"{label}.result.kind is invalid")

        jd_ids = block["jd_requirement_ids"]
        if not _strings(jd_ids):
            errors.append(f"{label}.jd_requirement_ids must be a unique string list")
        else:
            used = set(jd_ids)
            for requirement_id in sorted(used & unmatched_jd):
                errors.append(f"{label} uses unmatched JD requirement: {requirement_id}")
            unknown = used - matched_jd - unmatched_jd
            if jd_review.get("present") is True and unknown:
                errors.append(f"{label} uses unknown JD requirement: {sorted(unknown)[0]}")
            if jd_review.get("present") is False and used:
                errors.append(f"{label} cannot use JD requirements when no JD is present")

        integrity = block["integrity_review"]
        integrity_errors = _required_fields(
            integrity, set(INTEGRITY_CHECKS), f"{label}.integrity_review"
        )
        errors.extend(integrity_errors)
        if not integrity_errors and not all(
            integrity[field] is True for field in INTEGRITY_CHECKS
        ):
            errors.append(f"{label} integrity review must pass all checks")
        if block["approval_status"] != "user_approved":
            errors.append(f"{label}.approval_status must be user_approved")

    if len(block_ids) != len(set(block_ids)):
        errors.append("block IDs must be unique")

    approval = payload["copy_approval"]
    approval_errors = _required_fields(
        approval,
        {"status", "source", "approved_block_ids", "evidence_quote"},
        "copy_approval",
    )
    errors.extend(approval_errors)
    if not approval_errors:
        if approval["status"] != "user_approved":
            errors.append("copy approval status must be user_approved")
        if approval["source"] != "conversation":
            errors.append("copy approval must come from conversation")
        if not _text(approval["evidence_quote"]):
            errors.append("copy approval requires a conversational evidence quote")
        approved_ids = approval["approved_block_ids"]
        if not _strings(approved_ids) or set(approved_ids) != set(block_ids) or len(approved_ids) != len(block_ids):
            errors.append("approved_block_ids must exactly match reviewed block IDs")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an approved, evidence-linked content quality review"
    )
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"ERROR: could not read content quality review: {error}")
        return 1
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: content quality review is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
