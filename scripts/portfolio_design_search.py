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
WORD_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9+.#-]{1,30}")
_VENDOR_CORE: ModuleType | None = None


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
    args = parser.parse_args(argv)
    try:
        if args.command == "recommend":
            result = recommend(_read_json_object(args.input, "content map"))
        else:
            result = enrich(
                _read_json_object(args.input, "style brief"),
                _read_json_object(args.content_map, "content map"),
            )
        _atomic_write_json(args.output, result)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    except (OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
