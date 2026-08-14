from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import uuid
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import ModuleType
from typing import Any

from validate_design_catalog import validate_catalog
from validate_design_discovery import validate as validate_discovery_report


SKILL_ROOT = Path(__file__).resolve().parents[1]
CATALOG_ROOT = SKILL_ROOT / "vendor" / "ui-ux-pro-max"
VENDOR_CORE_PATH = CATALOG_ROOT / "src" / "core.py"
UPSTREAM = "nextlevelbuilder/ui-ux-pro-max-skill"
SENSITIVE_KEYS = {"name", "email", "phone", "address", "contact", "summary", "description", "body", "text"}
STYLE_LENSES = (
    "portfolio editorial asymmetric content first",
    "portfolio modular bento project showcase",
    "portfolio bold immersive experimental typography",
)
CATEGORY_DOMAINS = {
    "structure": ("landing", "style", "product", "ux"),
    "typography": ("typography", "style", "ux"),
    "color": ("color", "style", "ux"),
    "media": ("style", "product", "landing", "ux"),
    "primary_motion": ("motion", "style", "landing", "ux"),
    "secondary_motion": ("motion", "react", "ux"),
}
DOMAIN_ID_KEYS = {
    "landing": "Pattern Name",
    "style": "Style Category",
    "product": "Product Type",
    "typography": "Font Pairing Name",
    "color": "Product Type",
    "motion": "Category",
    "react": "Guideline",
    "ux": "Issue",
}
DOMAIN_QUERY_HINTS = {
    "motion": "scroll reveal hover stagger pin scrub interaction",
}
WORD_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9+.#-]{1,30}")
_VENDOR_CORE: ModuleType | None = None


class DesignCatalogInsufficient(RuntimeError):
    """Raised when a bounded catalog query cannot supply two candidates."""


def _load_vendor_core() -> ModuleType:
    global _VENDOR_CORE
    if _VENDOR_CORE is not None:
        return _VENDOR_CORE
    report = validate_catalog(CATALOG_ROOT)
    if not report.ok:
        raise RuntimeError("design catalog invalid: " + "; ".join(report.errors))
    spec = importlib.util.spec_from_file_location("resume_portfolio_vendor_core", VENDOR_CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load vendor core: {VENDOR_CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _VENDOR_CORE = module
    return module


def _string(value: object, default: str = "") -> str:
    return str(value).strip() if value is not None else default


def _mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: object) -> Sequence[object]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _safe_tokens(value: object) -> list[str]:
    if isinstance(value, Mapping):
        tokens: list[str] = []
        for key, child in value.items():
            if str(key).lower() not in SENSITIVE_KEYS:
                tokens.extend(_safe_tokens(child))
        return tokens
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        tokens = []
        for child in value:
            tokens.extend(_safe_tokens(child))
        return tokens
    return WORD_PATTERN.findall(_string(value))


def _unique_tokens(values: Sequence[str], limit: int = 24) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        normalized = value.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        output.append(value)
        if len(output) == limit:
            break
    return output


def _content_profile(content_map: Mapping[str, object]) -> dict[str, object]:
    profile = _mapping(content_map.get("profile"))
    projects = _sequence(content_map.get("projects"))
    skills = _sequence(content_map.get("skills"))
    media = _mapping(content_map.get("media"))
    role = _string(profile.get("role"), "portfolio professional")
    industry = _string(profile.get("industry"), "professional services")
    project_tokens: list[str] = []
    for project in projects:
        item = _mapping(project)
        project_tokens.extend(_safe_tokens(item.get("domain")))
        project_tokens.extend(_safe_tokens(item.get("technologies")))
    skill_tokens = _safe_tokens(skills)
    keywords = _unique_tokens([*project_tokens, *skill_tokens, "portfolio", "React"])
    density_score = len(projects) * 2 + len(skills)
    content_density = "high" if density_score >= 8 else "medium" if density_score >= 4 else "low"
    media_count = sum(
        1 if value is True else int(value) if isinstance(value, int) else 0
        for value in media.values()
    )
    media_profile = "rich" if media_count >= 4 else "limited" if media_count else "none"
    return {
        "role": role[:80],
        "industry": industry[:80],
        "content_density": content_density,
        "media_profile": media_profile,
        "keywords": keywords,
    }


def _query_text(profile: Mapping[str, object], extra: str = "") -> str:
    parts = [
        _string(profile.get("role")),
        _string(profile.get("industry")),
        *_sequence(profile.get("keywords")),
        _string(profile.get("content_density")),
        _string(profile.get("media_profile")),
        extra,
    ]
    return " ".join(_string(part) for part in parts if _string(part))


def _search(domain: str, query: str, count: int = 8) -> list[dict[str, str]]:
    result = _load_vendor_core().search(query, domain, count)
    if "error" in result:
        raise RuntimeError(_string(result["error"]))
    return [dict(item) for item in result.get("results", [])]


def _search_logical_domain(
    domain: str, query: str, count: int = 8
) -> list[dict[str, str]]:
    if domain == "motion":
        return _search("gsap", query, count)
    if domain == "react":
        result = _load_vendor_core().search_stack(query, "react", count)
        if "error" in result:
            raise RuntimeError(_string(result["error"]))
        return [dict(item) for item in result.get("results", [])]
    return _search(domain, query, count)


def _source_id(domain: str, row: Mapping[str, object], key: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", _string(row.get(key)).casefold()).strip("-")
    return f"{domain}:{value or 'unknown'}"


def _style_rows(query: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for lens in STYLE_LENSES:
        for row in _search("style", f"{query} {lens}", 16):
            family = _string(row.get("Style Category"))
            type_name = _string(row.get("Type")).casefold()
            compatibility = _string(row.get("Framework Compatibility")).casefold()
            if not family or family.casefold() in seen:
                continue
            if type_name in {"mobile", "bi/analytics"} or "react native" in compatibility:
                continue
            seen.add(family.casefold())
            rows.append(row)
    return rows


def _palette(row: Mapping[str, object]) -> list[str]:
    relationships = []
    for label, key in (("primary", "Primary"), ("accent", "Accent"), ("background", "Background"), ("foreground", "Foreground")):
        value = _string(row.get(key))
        if value:
            relationships.append(f"{label}: {value}")
    return relationships or [_string(row.get("Notes"), "Use one coherent accessible palette")]


def _media_strategy(profile: Mapping[str, object], style: Mapping[str, object]) -> str:
    media_profile = _string(profile.get("media_profile"))
    if media_profile == "rich":
        prefix = "Lead with authorized portrait and project media"
    elif media_profile == "limited":
        prefix = "Give the available project media one dominant role and use abstract fallbacks elsewhere"
    else:
        prefix = "Use typography, CSS geometry, and intentional whitespace instead of fabricated project imagery"
    return f"{prefix}; align treatment with {_string(style.get('Style Category'), 'the selected direction')}."


def direction_distance(left: Mapping[str, object], right: Mapping[str, object]) -> int:
    return sum(
        left.get(field) != right.get(field)
        for field in ("style_family", "composition", "surface_language")
    )


def _guardrails(query: str) -> list[str]:
    rows = _search("ux", f"{query} accessibility contrast focus responsive overflow", 6)
    return [
        f"{_string(row.get('Issue'))}: {_string(row.get('Do')) or _string(row.get('Description'))}"
        for row in rows
        if _string(row.get("Issue"))
    ][:6]


def _react_guidelines(query: str) -> list[str]:
    result = _load_vendor_core().search_stack(
        "memo rerender bundle image lazy loading components", "react", 5
    )
    if "error" in result:
        raise RuntimeError(_string(result["error"]))
    rows = [dict(item) for item in result.get("results", [])]
    return [
        f"{_string(row.get('Guideline'))}: {_string(row.get('Do')) or _string(row.get('Description'))}"
        for row in rows
        if _string(row.get("Guideline"))
    ][:5]


def recommend(content_map: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(content_map, Mapping):
        raise ValueError("content map must be a JSON object")
    profile = _content_profile(content_map)
    query = _query_text(profile)
    styles = _style_rows(query)
    landings = _search("landing", f"{query} portfolio hero project story", 12)
    colors = _search("color", f"{query} portfolio professional creative", 8)
    typography = _search("typography", f"{query} portfolio editorial technical", 8)
    products = _search("product", f"{query} portfolio developer freelancer", 6)
    if len(styles) < 3 or len(landings) < 3 or len(colors) < 3 or len(typography) < 3:
        raise RuntimeError("design catalog could not produce three complete candidate directions")

    candidates: list[dict[str, object]] = []
    for index, style in enumerate(styles):
        landing = landings[index % len(landings)]
        color = colors[index % len(colors)]
        type_row = typography[index % len(typography)]
        product = products[index % len(products)] if products else {}
        family = _string(style.get("Style Category"))
        candidate = {
            "id": f"direction-{len(candidates) + 1}",
            "name": family,
            "style_family": family.casefold(),
            "composition": f"{_string(landing.get('Pattern Name'))}: {_string(landing.get('Section Order'))}",
            "color_relationships": _palette(color),
            "typography_roles": {
                "display": _string(type_row.get("Heading Font"), "expressive display role"),
                "body": _string(type_row.get("Body Font"), "readable body role"),
                "hierarchy": _string(type_row.get("Notes"), _string(type_row.get("Mood/Style Keywords"))),
            },
            "surface_language": _string(style.get("CSS/Technical Keywords"), _string(style.get("Effects & Animation"))),
            "media_strategy": _media_strategy(profile, style),
            "fit_reasons": [
                _string(style.get("Best For")),
                _string(product.get("Key Considerations"), _string(product.get("Primary Style Recommendation"))),
            ],
            "risks": [
                _string(style.get("Do Not Use For"), "Avoid decorative excess that competes with resume evidence"),
                f"complexity: {_string(style.get('Complexity'), 'unknown')}; accessibility: {_string(style.get('Accessibility'), 'verify manually')}",
            ],
            "source_ids": [
                _source_id("style", style, "Style Category"),
                _source_id("landing", landing, "Pattern Name"),
                _source_id("color", color, "Product Type"),
                _source_id("typography", type_row, "Font Pairing Name"),
            ],
        }
        if all(direction_distance(candidate, existing) >= 2 for existing in candidates):
            candidates.append(candidate)
        if len(candidates) == 3:
            break
    if len(candidates) != 3:
        raise RuntimeError("design catalog candidates were not sufficiently distinct")

    return {
        "schema_version": 1,
        "mode": "recommend",
        "query": profile,
        "candidate_directions": candidates,
        "selected_direction_id": candidates[0]["id"],
        "guardrails": _guardrails(query),
        "react_guidelines": _react_guidelines(query),
        "provenance": {
            "upstream": UPSTREAM,
            "catalog_version": validate_catalog(CATALOG_ROOT).catalog_version,
            "domains": ["product", "style", "color", "typography", "landing", "ux", "react"],
        },
    }


def _approved_decision_ids(decisions: Mapping[str, object]) -> list[str]:
    result: list[str] = []
    for category in CATEGORY_DOMAINS:
        decision = _mapping(decisions.get(category))
        approval = _mapping(decision.get("approval"))
        if approval.get("status") != "user_approved":
            continue
        result.extend(
            _string(item)
            for item in _sequence(decision.get("selected_candidate_ids"))
            if _string(item)
        )
    return result


def _category_query_context(
    content_map: Mapping[str, object],
    baseline: Mapping[str, object],
    decisions: Mapping[str, object],
) -> dict[str, object]:
    profile = _content_profile(content_map)
    return {
        **profile,
        "baseline_direction_id": _string(baseline.get("selected_direction_id")),
        "approved_decision_ids": _approved_decision_ids(decisions),
    }


def build_baseline(
    content_map: Mapping[str, object],
    reference_selection: Mapping[str, object] | None = None,
) -> dict[str, object]:
    report = recommend(content_map)
    report["mode"] = "baseline"
    report["report_type"] = "baseline"
    report["reference_selection_ids"] = _unique_tokens(
        _safe_tokens(reference_selection or {}), limit=8
    )
    return report


def _row_label(domain: str, row: Mapping[str, object]) -> str:
    return _string(row.get(DOMAIN_ID_KEYS[domain]), domain)


def _row_notes(row: Mapping[str, object]) -> list[str]:
    keys = (
        "Best For",
        "Description",
        "Do",
        "Notes",
        "Key Considerations",
        "Effects & Animation",
        "Mood/Style Keywords",
        "Guideline",
        "Performance Notes",
    )
    return [_string(row.get(key)) for key in keys if _string(row.get(key))]


def _category_candidate(
    category: str,
    index: int,
    rows: Mapping[str, Mapping[str, object]],
    inherited_ids: Sequence[str],
) -> dict[str, object]:
    source_ids = [
        _source_id(domain, row, DOMAIN_ID_KEYS[domain])
        for domain, row in rows.items()
        if row
    ]
    labels = [_row_label(domain, row) for domain, row in rows.items() if row]
    notes = [note for row in rows.values() for note in _row_notes(row)]
    accessibility = [
        note
        for note in notes
        if any(
            term in note.casefold()
            for term in ("access", "contrast", "focus", "motion", "touch")
        )
    ][:3]
    return {
        "id": f"{category}-{index + 1}",
        "label": " · ".join(labels[:2]),
        "fit": notes[:2] or [f"Catalog fit for {category}"],
        "risks": notes[2:4]
        or ["Verify content fit and implementation cost"],
        "tradeoffs": notes[4:6]
        or ["Balance expression, readability, and cost"],
        "compatibility": list(inherited_ids),
        "responsive_fallback": (
            "Preserve semantic order in a single-column document flow"
        ),
        "accessibility_notes": accessibility
        or ["Verify focus, contrast, touch, and reduced-motion behavior"],
        "source_ids": source_ids,
    }


def _category_candidates(
    category: str,
    query: str,
    inherited_ids: Sequence[str],
) -> list[dict[str, object]]:
    domains = CATEGORY_DOMAINS[category]
    rows_by_domain = {
        domain: _search_logical_domain(
            domain,
            " ".join(filter(None, (query, DOMAIN_QUERY_HINTS.get(domain, "")))),
            8,
        )
        for domain in domains
    }
    available = min((len(rows) for rows in rows_by_domain.values()), default=0)
    return [
        _category_candidate(
            category,
            index,
            {domain: rows[index] for domain, rows in rows_by_domain.items()},
            inherited_ids,
        )
        for index in range(min(available, 3))
    ]


def search_category(
    category: str,
    content_map: Mapping[str, object],
    baseline: Mapping[str, object],
    decisions: Mapping[str, object],
) -> dict[str, object]:
    if category not in CATEGORY_DOMAINS:
        raise ValueError(f"unsupported design category: {category}")
    if not isinstance(content_map, Mapping):
        raise ValueError("content map must be a JSON object")
    if not isinstance(baseline, Mapping):
        raise ValueError("baseline must be a JSON object")
    if not isinstance(decisions, Mapping):
        raise ValueError("decisions must be a JSON object")

    context = _category_query_context(content_map, baseline, decisions)
    inherited_ids = list(context["approved_decision_ids"])
    full_query = _query_text(
        context,
        " ".join(
            [
                category,
                _string(context["baseline_direction_id"]),
                *inherited_ids,
            ]
        ),
    )
    candidates = _category_candidates(category, full_query, inherited_ids)
    if len(candidates) < 2:
        broad_query = " ".join(
            filter(
                None,
                (
                    _string(context["role"]),
                    _string(context["industry"]),
                    _string(context["content_density"]),
                    _string(context["media_profile"]),
                    _string(context["baseline_direction_id"]),
                    *inherited_ids,
                    category,
                ),
            )
        )
        candidates = _category_candidates(category, broad_query, inherited_ids)
    if len(candidates) < 2:
        raise DesignCatalogInsufficient(
            "design_catalog_insufficient: "
            f"category={category}; domains={','.join(CATEGORY_DOMAINS[category])}; "
            f"found={len(candidates)}; required=2"
        )
    return {
        "schema_version": 1,
        "report_type": "category",
        "category": category,
        "query_context": context,
        "domains_searched": list(CATEGORY_DOMAINS[category]),
        "inherited_decision_ids": inherited_ids,
        "candidates": candidates,
        "recommended_candidate_id": candidates[0]["id"],
        "provenance": {
            "upstream": UPSTREAM,
            "catalog_version": validate_catalog(CATALOG_ROOT).catalog_version,
        },
    }


def aggregate_discovery(
    content_map: Mapping[str, object],
    baseline: Mapping[str, object],
    category_reports: Mapping[str, object],
    design_spec: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(content_map, Mapping):
        raise ValueError("content map must be a JSON object")
    if validate_discovery_report(baseline, expected_type="baseline"):
        raise ValueError("baseline design discovery report is invalid")
    decisions = _mapping(design_spec.get("decisions"))
    approved_decisions: dict[str, object] = {}
    for category in CATEGORY_DOMAINS:
        report = _mapping(category_reports.get(category))
        errors = validate_discovery_report(report, expected_type="category")
        if errors or report.get("category") != category:
            raise ValueError(f"invalid category report: {category}")
        decision = _mapping(decisions.get(category))
        approval = _mapping(decision.get("approval"))
        if approval.get("status") != "user_approved":
            raise ValueError(f"category is not user approved: {category}")
        selected_ids = [
            _string(item)
            for item in _sequence(decision.get("selected_candidate_ids"))
            if _string(item)
        ]
        candidates = [
            _mapping(item) for item in _sequence(report.get("candidates"))
        ]
        candidate_by_id = {
            _string(candidate.get("id")): candidate for candidate in candidates
        }
        if decision.get("status") != "skipped":
            if not selected_ids or not set(selected_ids) <= set(candidate_by_id):
                raise ValueError(
                    f"approved IDs do not reference {category} candidates"
                )
        report_path = _string(decision.get("discovery_report")) or (
            ".resume-site-work/reports/design-discovery/"
            f"{category.replace('_', '-')}.json"
        )
        approved_decisions[category] = {
            "status": _string(decision.get("status"), "confirmed"),
            "selected_candidate_ids": selected_ids,
            "selected_candidates": [
                dict(candidate_by_id[candidate_id])
                for candidate_id in selected_ids
            ],
            "discovery_report": report_path,
        }
    return {
        "schema_version": 1,
        "mode": "approved-discovery",
        "query": _content_profile(content_map),
        "baseline": dict(baseline),
        "approved_decisions": approved_decisions,
        "guardrails": list(_sequence(baseline.get("guardrails"))),
        "react_guidelines": list(
            _sequence(baseline.get("react_guidelines"))
        ),
        "provenance": dict(_mapping(baseline.get("provenance"))),
    }


def enrich(style_brief: Mapping[str, object], content_map: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(style_brief, Mapping):
        raise ValueError("style brief must be a JSON object")
    if not isinstance(content_map, Mapping):
        raise ValueError("content map must be a JSON object")
    profile = _content_profile(content_map)
    typography = _mapping(style_brief.get("typography"))
    brief_query = " ".join(
        _string(style_brief.get(key))
        for key in ("direction", "spacing_density", "grid_and_composition", "surface_language", "decorative_language")
    )
    query = _query_text(profile, brief_query)
    styles = _style_rows(query)
    colors = _search("color", query, 3)
    type_rows = _search("typography", query, 3)
    source_ids = []
    if styles:
        source_ids.append(_source_id("style", styles[0], "Style Category"))
    if colors:
        source_ids.append(_source_id("color", colors[0], "Product Type"))
    if type_rows:
        source_ids.append(_source_id("typography", type_rows[0], "Font Pairing Name"))
    candidate = {
        "id": "reference-direction",
        "name": _string(style_brief.get("direction"), "Reference-derived direction"),
        "style_family": _string(style_brief.get("direction"), "reference-derived").casefold(),
        "composition": _string(style_brief.get("grid_and_composition")),
        "color_relationships": [_string(item) for item in _sequence(style_brief.get("color_relationships"))],
        "typography_roles": {
            "display": _string(typography.get("display")),
            "body": _string(typography.get("body")),
            "hierarchy": _string(typography.get("hierarchy")),
        },
        "surface_language": _string(style_brief.get("surface_language")),
        "media_strategy": _string(style_brief.get("imagery")),
        "fit_reasons": [_string(item) for item in _sequence(style_brief.get("adopt"))],
        "risks": [_string(item) for item in _sequence(style_brief.get("avoid_literal_copying"))],
        "source_ids": source_ids or ["reference:visible-evidence"],
    }
    return {
        "schema_version": 1,
        "mode": "enrich",
        "query": profile,
        "candidate_directions": [candidate],
        "selected_direction_id": candidate["id"],
        "guardrails": _guardrails(query),
        "react_guidelines": _react_guidelines(query),
        "reference_evidence_priority": True,
        "provenance": {
            "upstream": UPSTREAM,
            "catalog_version": validate_catalog(CATALOG_ROOT).catalog_version,
            "domains": ["style", "color", "typography", "ux", "react"],
        },
    }


def _read_json_object(path: Path, label: str) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid {label}: {error}") from error
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _atomic_write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate portfolio design intelligence.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    recommend_parser = subparsers.add_parser("recommend")
    recommend_parser.add_argument("--input", type=Path, required=True)
    recommend_parser.add_argument("--output", type=Path, required=True)
    enrich_parser = subparsers.add_parser("enrich")
    enrich_parser.add_argument("--input", type=Path, required=True)
    enrich_parser.add_argument("--content-map", type=Path, required=True)
    enrich_parser.add_argument("--output", type=Path, required=True)
    baseline_parser = subparsers.add_parser("baseline")
    baseline_parser.add_argument("--content-map", type=Path, required=True)
    baseline_parser.add_argument("--reference-selection", type=Path)
    baseline_parser.add_argument("--output", type=Path, required=True)
    category_parser = subparsers.add_parser("category")
    category_parser.add_argument(
        "--category", choices=tuple(CATEGORY_DOMAINS), required=True
    )
    category_parser.add_argument("--content-map", type=Path, required=True)
    category_parser.add_argument("--baseline", type=Path, required=True)
    category_parser.add_argument("--decisions", type=Path, required=True)
    category_parser.add_argument("--output", type=Path, required=True)
    aggregate_parser = subparsers.add_parser("aggregate")
    aggregate_parser.add_argument("--content-map", type=Path, required=True)
    aggregate_parser.add_argument("--baseline", type=Path, required=True)
    aggregate_parser.add_argument("--reports-dir", type=Path, required=True)
    aggregate_parser.add_argument("--site-design-spec", type=Path, required=True)
    aggregate_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "recommend":
            result = recommend(_read_json_object(args.input, "content map"))
        elif args.command == "enrich":
            result = enrich(
                _read_json_object(args.input, "style brief"),
                _read_json_object(args.content_map, "content map"),
            )
        elif args.command == "baseline":
            reference_selection = (
                _read_json_object(args.reference_selection, "reference selection")
                if args.reference_selection
                else None
            )
            result = build_baseline(
                _read_json_object(args.content_map, "content map"),
                reference_selection,
            )
        elif args.command == "category":
            result = search_category(
                args.category,
                _read_json_object(args.content_map, "content map"),
                _read_json_object(args.baseline, "baseline"),
                _read_json_object(args.decisions, "decisions"),
            )
        else:
            reports = {
                category: _read_json_object(
                    args.reports_dir / f"{category.replace('_', '-')}.json",
                    f"{category} category report",
                )
                for category in CATEGORY_DOMAINS
            }
            result = aggregate_discovery(
                _read_json_object(args.content_map, "content map"),
                _read_json_object(args.baseline, "baseline"),
                reports,
                _read_json_object(args.site_design_spec, "site design spec"),
            )
        _atomic_write_json(args.output, result)
    except DesignCatalogInsufficient as error:
        print(str(error), file=sys.stderr)
        return 3
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    except (OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
