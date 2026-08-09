from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT_FIELDS = {
    "schema_version",
    "identity_strategy",
    "signature",
    "layout",
    "typography",
    "color",
    "surface",
    "motion",
    "anti_template_rules",
    "acceptance_checks",
    "traceability",
}
DESIGN_SECTIONS = ROOT_FIELDS - {"schema_version", "traceability"}
SECTION_FIELDS = {
    "identity_strategy": {
        "audience",
        "narrative_priorities",
        "density",
        "content_form_relationships",
    },
    "signature": {
        "visual_protagonist",
        "composition_commitment",
        "structural_device",
        "template_independence_claim",
    },
    "layout": {
        "hierarchy",
        "section_rhythm",
        "alignment_logic",
        "density_ranges",
        "responsive_transformations",
        "prohibited_arrangements",
    },
    "typography": {
        "roles",
        "scale_relationships",
        "measure",
        "rhythm",
        "contrast",
        "fallbacks",
    },
    "color": {
        "semantic_roles",
        "proportion_guidance",
        "contrast_targets",
        "surface_relationships",
        "prohibited_effects",
    },
    "surface": {
        "container_rules",
        "border_rules",
        "radius_rules",
        "shadow_rules",
        "texture_rules",
        "repetition_rules",
    },
    "motion": {
        "primary_system",
        "secondary_effects",
        "purposes",
        "controller_ownership",
        "reduced_motion",
        "coarse_pointer",
        "fallbacks",
    },
}
STRING_FIELDS = {
    "identity_strategy": {"audience", "density"},
    "signature": SECTION_FIELDS["signature"],
    "layout": {"alignment_logic"},
    "motion": {"primary_system"},
}
ACCEPTANCE_GROUPS = {
    "identity_fit",
    "aesthetic_quality",
    "accessibility",
    "responsive",
    "runtime_safety",
}
ALLOWED_SEVERITIES = {"blocking", "repairable", "advisory"}
RULE_FIELDS = {"rule_id", "criterion", "evidence_required", "severity"}
TRACE_FIELDS = {
    "contract_path",
    "source_decision_ids",
    "creative_direction_paths",
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


def _string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(_string(item) for item in value)
        and len({item.strip().casefold() for item in value}) == len(value)
    )


def _walk(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    items = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            items.extend(_walk(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_walk(child, f"{path}[{index}]"))
    return items


def _validate_section(report: dict[str, Any], section: str) -> list[str]:
    value = report[section]
    if not isinstance(value, dict) or set(value) != SECTION_FIELDS[section]:
        return [
            f"{section} must contain exactly: "
            + ", ".join(sorted(SECTION_FIELDS[section]))
        ]
    errors: list[str] = []
    string_fields = STRING_FIELDS.get(section, set())
    for field in SECTION_FIELDS[section]:
        if field in string_fields:
            if not _string(value[field]):
                errors.append(f"{section}.{field} must be a non-empty string")
        elif section == "motion" and field == "secondary_effects":
            effects = value[field]
            if not isinstance(effects, list) or not all(_string(item) for item in effects):
                errors.append("motion.secondary_effects must be a string list")
            elif len({item.strip().casefold() for item in effects}) != len(effects):
                errors.append("motion.secondary_effects must contain unique entries")
        elif not _string_list(value[field]):
            errors.append(f"{section}.{field} must be a non-empty unique string list")
    return errors


def _validate_rule(value: Any, path: str, rule_ids: set[str]) -> list[str]:
    if not isinstance(value, dict) or set(value) != RULE_FIELDS:
        return [f"{path} must contain exactly: " + ", ".join(sorted(RULE_FIELDS))]
    errors: list[str] = []
    for field in ("rule_id", "criterion"):
        if not _string(value[field]):
            errors.append(f"{path}.{field} must be a non-empty string")
    if not _string_list(value["evidence_required"]):
        errors.append(f"{path}.evidence_required must be a non-empty unique string list")
    if value["severity"] not in ALLOWED_SEVERITIES:
        errors.append(f"{path}.severity must be blocking, repairable, or advisory")
    if _string(value["rule_id"]):
        rule_id = value["rule_id"].strip()
        if rule_id in rule_ids:
            errors.append(f"duplicate rule_id: {rule_id}")
        rule_ids.add(rule_id)
    return errors


def validate(report: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(report, dict):
        return ["report must be a JSON object"]
    if set(report) != ROOT_FIELDS:
        missing = ROOT_FIELDS - set(report)
        extra = set(report) - ROOT_FIELDS
        if missing:
            errors.append("missing root fields: " + ", ".join(sorted(missing)))
        if extra:
            errors.append("unknown root fields: " + ", ".join(sorted(extra)))
        return errors
    if report["schema_version"] != 1:
        errors.append("schema_version must be 1")

    for section in SECTION_FIELDS:
        errors.extend(_validate_section(report, section))

    rule_ids: set[str] = set()
    anti_template = report["anti_template_rules"]
    if not isinstance(anti_template, list) or not anti_template:
        errors.append("anti_template_rules must be a non-empty list")
    else:
        for index, item in enumerate(anti_template):
            errors.extend(
                _validate_rule(item, f"anti_template_rules[{index}]", rule_ids)
            )

    checks = report["acceptance_checks"]
    if not isinstance(checks, dict) or set(checks) != ACCEPTANCE_GROUPS:
        errors.append(
            "acceptance_checks must contain exactly: "
            + ", ".join(sorted(ACCEPTANCE_GROUPS))
        )
    else:
        for group in sorted(ACCEPTANCE_GROUPS):
            values = checks[group]
            if not isinstance(values, list) or not values:
                errors.append(f"acceptance_checks.{group} must be a non-empty list")
                continue
            for index, item in enumerate(values):
                errors.extend(
                    _validate_rule(
                        item,
                        f"acceptance_checks.{group}[{index}]",
                        rule_ids,
                    )
                )

    traceability = report["traceability"]
    covered: set[str] = set()
    if not isinstance(traceability, list) or not traceability:
        errors.append("traceability must be a non-empty list")
    else:
        for index, item in enumerate(traceability):
            path = f"traceability[{index}]"
            if not isinstance(item, dict) or set(item) != TRACE_FIELDS:
                errors.append(
                    f"{path} must contain exactly: "
                    + ", ".join(sorted(TRACE_FIELDS))
                )
                continue
            contract_path = item["contract_path"]
            if not _string(contract_path) or contract_path not in DESIGN_SECTIONS:
                errors.append(f"unknown contract_path: {contract_path}")
            else:
                covered.add(contract_path)
            for field in ("source_decision_ids", "creative_direction_paths"):
                if not _string_list(item[field]):
                    errors.append(f"{path}.{field} must be a non-empty unique string list")
    for section in sorted(DESIGN_SECTIONS - covered):
        errors.append(f"traceability must cover {section}")

    for path, value in _walk(report):
        key = path.rsplit(".", 1)[-1].casefold()
        if key in FORBIDDEN_KEYS:
            errors.append(f"implementation payload key is not allowed: {path}")
        if isinstance(value, str) and IMPLEMENTATION_PATTERN.search(value):
            errors.append(f"implementation payload is not allowed: {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a portfolio design contract.")
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
    print("OK: design-contract report is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
