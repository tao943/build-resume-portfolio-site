from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SEARCH_PATH = SCRIPT_DIR / "portfolio_design_search.py"

CONTENT_MAP = {
    "profile": {
        "name": "Private Person",
        "role": "AI application developer",
        "industry": "technology",
        "summary": "Builds agent systems and content-driven React products.",
    },
    "projects": [
        {
            "title": "Agent Runtime",
            "domain": "developer tools",
            "technologies": ["Python", "React", "RAG"],
        },
        {
            "title": "Local Knowledge Search",
            "domain": "AI search",
            "technologies": ["FastAPI", "vector search"],
        },
    ],
    "skills": ["React", "Python", "AI agents", "product engineering"],
    "media": {"portrait": False, "project_images": 1, "video": False},
    "contact": {"email": "person@example.com", "phone": "13800138000"},
}

STYLE_BRIEF = {
    "direction": "Warm technical editorial",
    "color_relationships": ["warm paper background", "ink text", "teal accent"],
    "typography": {
        "display": "editorial serif display",
        "body": "quiet sans body",
        "hierarchy": "large contrast with compact metadata",
    },
    "spacing_density": "spacious sections with dense project details",
    "grid_and_composition": "asymmetric editorial grid with oversized project media",
    "surface_language": "thin rules and flat panels",
    "imagery": "wide crops with restrained color grading",
    "decorative_language": "fine rules and isolated geometric marks",
    "adopt": ["strong editorial rhythm"],
    "avoid_literal_copying": ["logos", "exact composition"],
}


def load_search_module():
    if not SEARCH_PATH.is_file():
        raise AssertionError(f"missing design search adapter: {SEARCH_PATH}")
    spec = importlib.util.spec_from_file_location("portfolio_design_search", SEARCH_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("unable to load design search adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PortfolioDesignSearchTests(unittest.TestCase):
    def test_recommend_returns_three_distinct_privacy_safe_directions(self) -> None:
        module = load_search_module()

        result = module.recommend(CONTENT_MAP)

        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["mode"], "recommend")
        directions = result["candidate_directions"]
        self.assertEqual(len(directions), 3)
        self.assertEqual(len({item["style_family"] for item in directions}), 3)
        self.assertIn(result["selected_direction_id"], {item["id"] for item in directions})
        for left_index, left in enumerate(directions):
            for right in directions[left_index + 1 :]:
                self.assertGreaterEqual(module.direction_distance(left, right), 2)
        serialized = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("person@example.com", serialized)
        self.assertNotIn("13800138000", serialized)
        self.assertNotIn("Private Person", serialized)
        self.assertEqual(result["provenance"]["catalog_version"], "2.11.0")

    def test_each_direction_is_a_complete_design_bundle(self) -> None:
        module = load_search_module()
        required = {
            "id",
            "name",
            "style_family",
            "composition",
            "color_relationships",
            "typography_roles",
            "surface_language",
            "media_strategy",
            "fit_reasons",
            "risks",
            "source_ids",
        }

        result = module.recommend(CONTENT_MAP)

        for direction in result["candidate_directions"]:
            self.assertTrue(required.issubset(direction), direction)
            self.assertTrue(direction["source_ids"])

    def test_enrich_preserves_reference_visual_evidence(self) -> None:
        module = load_search_module()

        result = module.enrich(STYLE_BRIEF, CONTENT_MAP)

        self.assertEqual(result["mode"], "enrich")
        self.assertTrue(result["reference_evidence_priority"])
        selected = result["candidate_directions"][0]
        self.assertEqual(selected["name"], STYLE_BRIEF["direction"])
        self.assertEqual(selected["composition"], STYLE_BRIEF["grid_and_composition"])
        self.assertEqual(selected["surface_language"], STYLE_BRIEF["surface_language"])
        self.assertEqual(selected["media_strategy"], STYLE_BRIEF["imagery"])
        self.assertTrue(result["guardrails"])
        self.assertTrue(result["react_guidelines"])

    def test_recommend_rejects_non_object_input(self) -> None:
        module = load_search_module()

        with self.assertRaisesRegex(ValueError, "content map must be a JSON object"):
            module.recommend([])


if __name__ == "__main__":
    unittest.main()
