from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import portfolio_design_search as search  # noqa: E402
import validate_design_discovery as discovery_validator  # noqa: E402


def _direction(index: int) -> dict[str, object]:
    return {
        "id": f"direction-{index}",
        "name": f"Direction {index}",
        "style_family": "editorial" if index == 1 else f"family-{index}",
        "composition": "asymmetric project narrative",
        "color_relationships": ["primary: #111111", "accent: #ff5a36"],
        "typography_roles": {
            "display": "editorial display",
            "body": "readable sans",
            "hierarchy": "strong numbered hierarchy",
        },
        "surface_language": "flat high-contrast surfaces",
        "media_strategy": "Use authorized project evidence as the visual lead.",
        "fit_reasons": ["Fits a project-led technical portfolio."],
        "risks": ["Avoid equal-weight project cards."],
        "source_ids": [
            f"style:editorial-{index}",
            f"landing:project-story-{index}",
        ],
    }


def _baseline() -> dict[str, object]:
    return {
        "schema_version": 1,
        "report_type": "baseline",
        "mode": "baseline",
        "query": {
            "role": "frontend engineer",
            "industry": "developer tools",
            "content_density": "high",
            "media_profile": "limited",
            "keywords": ["React", "design systems"],
        },
        "candidate_directions": [_direction(1), _direction(2), _direction(3)],
        "selected_direction_id": "direction-1",
        "guardrails": ["Preserve readable hierarchy."],
        "react_guidelines": ["Keep component ownership explicit."],
        "reference_selection_ids": ["reference:project-process"],
        "provenance": {
            "upstream": "nextlevelbuilder/ui-ux-pro-max-skill",
            "catalog_version": "test-catalog",
        },
    }


def _content_map() -> dict[str, object]:
    return {
        "profile": {
            "role": "frontend engineer",
            "industry": "developer tools",
        },
        "projects": [
            {"domain": "design systems", "technologies": ["React", "CSS"]}
        ],
        "skills": ["interaction design", "accessibility"],
        "media": {"project_images": 1},
    }


class EarlyAntiTemplateBaselineTests(unittest.TestCase):
    def test_builds_valid_provisional_baseline(self) -> None:
        report = search.build_anti_template_baseline(_content_map(), _baseline())

        self.assertEqual(report["report_type"], "anti_template_baseline")
        self.assertEqual(report["status"], "provisional_unapproved")
        self.assertTrue(report["evidence_ids"])
        self.assertEqual(
            set(report["category_obligations"]), set(search.CATEGORY_DOMAINS)
        )
        self.assertEqual(
            discovery_validator.validate(report, "anti_template_baseline"), []
        )

    def test_rejects_missing_evidence(self) -> None:
        report = search.build_anti_template_baseline(_content_map(), _baseline())
        invalid = copy.deepcopy(report)
        invalid["evidence_ids"] = []

        self.assertIn(
            "anti-template baseline requires evidence_ids",
            discovery_validator.validate(invalid, "anti_template_baseline"),
        )


if __name__ == "__main__":
    unittest.main()
