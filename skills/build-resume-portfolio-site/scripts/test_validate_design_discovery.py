from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_design_discovery import validate


VALID_CANDIDATE = {
    "id": "typography-1",
    "label": "Editorial Serif · Quiet Sans",
    "fit": ["Readable technical editorial hierarchy"],
    "risks": ["Verify Chinese fallback metrics"],
    "tradeoffs": ["Distinctive headings with restrained body text"],
    "compatibility": ["structure-editorial-grid"],
    "responsive_fallback": "Single-column document flow",
    "accessibility_notes": ["Preserve contrast and readable line length"],
    "source_ids": ["typography:editorial-serif", "style:editorial"],
}

VALID_CATEGORY = {
    "schema_version": 1,
    "report_type": "category",
    "category": "typography",
    "query_context": {
        "role": "AI application developer",
        "industry": "technology",
        "content_density": "high",
        "media_profile": "limited",
        "keywords": ["React", "Python"],
        "baseline_direction_id": "direction-1",
        "approved_decision_ids": ["structure-editorial-grid"],
    },
    "domains_searched": ["typography", "style", "ux"],
    "inherited_decision_ids": ["structure-editorial-grid"],
    "candidates": [
        VALID_CANDIDATE,
        {**VALID_CANDIDATE, "id": "typography-2", "label": "Technical Sans"},
    ],
    "recommended_candidate_id": "typography-1",
    "provenance": {
        "upstream": "nextlevelbuilder/ui-ux-pro-max-skill",
        "catalog_version": "2.11.0",
    },
}

VALID_DIRECTION = {
    "id": "direction-1",
    "name": "Editorial",
    "style_family": "editorial",
    "composition": "Asymmetric project narrative",
    "color_relationships": ["paper background", "ink foreground"],
    "typography_roles": {
        "display": "serif",
        "body": "sans",
        "hierarchy": "high contrast",
    },
    "surface_language": "flat panels and fine rules",
    "media_strategy": "one dominant authorized project image",
    "fit_reasons": ["content-first portfolio"],
    "risks": ["mobile fallback required"],
    "source_ids": ["style:editorial", "landing:portfolio-story"],
}

VALID_BASELINE = {
    "schema_version": 1,
    "report_type": "baseline",
    "mode": "baseline",
    "query": {
        "role": "AI application developer",
        "industry": "technology",
        "content_density": "high",
        "media_profile": "limited",
        "keywords": ["React", "Python"],
    },
    "candidate_directions": [
        VALID_DIRECTION,
        {**VALID_DIRECTION, "id": "direction-2", "name": "Modular"},
        {**VALID_DIRECTION, "id": "direction-3", "name": "Immersive"},
    ],
    "selected_direction_id": "direction-1",
    "guardrails": [],
    "react_guidelines": [],
    "reference_selection_ids": [],
    "provenance": {
        "upstream": "nextlevelbuilder/ui-ux-pro-max-skill",
        "catalog_version": "2.11.0",
        "domains": ["style", "landing", "color", "typography"],
    },
}


class ValidateDesignDiscoveryTests(unittest.TestCase):
    def test_valid_baseline_report_passes(self) -> None:
        self.assertEqual(validate(deepcopy(VALID_BASELINE)), [])

    def test_valid_category_report_passes(self) -> None:
        self.assertEqual(validate(deepcopy(VALID_CATEGORY)), [])

    def test_candidate_without_source_ids_fails(self) -> None:
        payload = deepcopy(VALID_CATEGORY)
        payload["candidates"][0]["source_ids"] = []
        self.assertIn("candidate typography-1 requires source_ids", validate(payload))

    def test_category_with_wrong_domains_fails(self) -> None:
        payload = deepcopy(VALID_CATEGORY)
        payload["domains_searched"] = ["color"]
        self.assertIn("typography domains do not match contract", validate(payload))

    def test_duplicate_candidate_ids_fail(self) -> None:
        payload = deepcopy(VALID_CATEGORY)
        payload["candidates"][1]["id"] = "typography-1"
        self.assertIn("candidate IDs must be unique", validate(payload))

    def test_inherited_decisions_must_match_query_context(self) -> None:
        payload = deepcopy(VALID_CATEGORY)
        payload["query_context"]["approved_decision_ids"] = []
        self.assertIn(
            "inherited decisions do not match query context", validate(payload)
        )

    def test_baseline_requires_exactly_three_directions(self) -> None:
        payload = deepcopy(VALID_BASELINE)
        payload["candidate_directions"].pop()
        self.assertIn("baseline requires exactly three directions", validate(payload))

    def test_privacy_sensitive_keys_are_rejected(self) -> None:
        payload = deepcopy(VALID_CATEGORY)
        payload["query_context"]["email"] = "person@example.com"
        self.assertIn("privacy-sensitive key is not allowed: email", validate(payload))


if __name__ == "__main__":
    unittest.main()
