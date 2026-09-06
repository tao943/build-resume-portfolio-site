from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import portfolio_design_search as search  # noqa: E402
import validate_creative_direction as creative_validator  # noqa: E402
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


def _candidate(category: str, index: int) -> dict[str, object]:
    return {
        "id": f"{category}-{index}",
        "label": f"{category.title()} option {index}",
        "fit": ["Strengthens the evidence-led hierarchy."],
        "risks": ["Requires responsive verification."],
        "tradeoffs": ["Balances expression and readability."],
        "compatibility": [],
        "responsive_fallback": "Preserve semantic order in one column.",
        "accessibility_notes": ["Preserve focus and reduced motion."],
        "source_ids": [f"style:{category}-{index}"],
    }


def _approved_design_spec() -> dict[str, object]:
    return {
        "decisions": {
            category: {
                "status": "confirmed",
                "selected_candidate_ids": [f"{category}-1"],
                "discovery_report": (
                    ".resume-site-work/reports/design-discovery/"
                    f"{category.replace('_', '-')}.json"
                ),
                "approval": {"status": "user_approved"},
            }
            for category in search.CATEGORY_DOMAINS
        }
    }


def _creative_direction() -> dict[str, object]:
    return {
        "schema_version": 1,
        "creative_thesis": "Project decisions become the visible design system.",
        "experience_priority": ["Project evidence", "Engineering judgment"],
        "creative_freedom": {
            "fixed": ["Preserve approved project evidence"],
            "open": {
                "composition": ["Asymmetric evidence narrative"],
                "layout_patterns": ["Persistent project index"],
                "motion_language": ["Progressive narrative motion"],
                "visual_metaphor": ["Decision trail"],
                "surface_treatment": ["High-contrast editorial surfaces"],
            },
            "avoid": ["Equal-weight generic cards"],
        },
        "layout_candidates": [
            {
                "id": "layout-1",
                "family": "editorial",
                "fit": "Makes evidence primary.",
                "risks": ["Needs careful mobile ordering."],
                "responsive_fallback": "Keep the project index before details.",
            },
            {
                "id": "layout-2",
                "family": "split narrative",
                "fit": "Separates decisions from results.",
                "risks": ["May require more scrolling."],
                "responsive_fallback": "Stack paired evidence in semantic order.",
            },
        ],
        "selected_candidate_id": "layout-1",
        "selection_rationale": "Best preserves the approved evidence hierarchy.",
        "concept_prototype": {
            "visual_protagonist": "The project decision trail.",
            "composition_commitment": "An asymmetric indexed narrative.",
            "type_color_character": "Editorial contrast with restrained accent.",
            "representative_interaction_state": "Active project index state.",
            "template_independence_test": "The index remains recognizable without motion.",
            "deferred_to_later": ["Final media crop details"],
        },
        "responsive_freedom": {
            "must_preserve": ["Project index prominence"],
            "may_adapt": ["Column count"],
        },
        "motion_freedom": {
            "purpose": "Reveal causal project progression.",
            "allowed": ["Index-linked transitions"],
            "avoid": ["Uniform section reveals"],
        },
        "review_questions": [
            "Is the project evidence dominant?",
            "Does the index remain recognizable?",
            "Does motion clarify progression?",
        ],
        "anti_template_resolutions": [
            {
                "rule_id": "anti-template.no-equal-card-grid",
                "status": "adopted",
                "approved_candidate_ids": ["structure-1"],
                "evidence_ids": ["style:editorial-1"],
                "rationale": "The approved structure uses unequal evidence hierarchy.",
            }
        ],
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

    def test_category_inherits_anti_template_rules_and_obligation(self) -> None:
        anti_template = search.build_anti_template_baseline(
            _content_map(), _baseline()
        )
        with patch.object(
            search,
            "_category_candidates",
            return_value=[_candidate("structure", 1), _candidate("structure", 2)],
        ):
            report = search.search_category(
                "structure", _content_map(), _baseline(), anti_template, {}
            )

        self.assertEqual(
            report["anti_template_baseline_id"], anti_template["id"]
        )
        self.assertTrue(
            report["candidates"][0]["anti_template_evaluation"][
                "baseline_rule_ids"
            ]
        )
        self.assertEqual(discovery_validator.validate(report, "category"), [])

    def test_category_validation_rejects_broken_traceability(self) -> None:
        anti_template = search.build_anti_template_baseline(
            _content_map(), _baseline()
        )
        with patch.object(
            search,
            "_category_candidates",
            return_value=[_candidate("color", 1), _candidate("color", 2)],
        ):
            report = search.search_category(
                "color", _content_map(), _baseline(), anti_template, {}
            )

        missing_id = copy.deepcopy(report)
        missing_id["anti_template_baseline_id"] = ""
        self.assertIn(
            "category requires anti_template_baseline_id",
            discovery_validator.validate(missing_id, "category"),
        )

        unknown_rule = copy.deepcopy(report)
        unknown_rule["candidates"][0]["anti_template_evaluation"][
            "baseline_rule_ids"
        ] = ["anti-template.unknown"]
        self.assertIn(
            "candidate color-1 references unknown anti-template rules",
            discovery_validator.validate(unknown_rule, "category"),
        )

        missing_obligation = copy.deepcopy(report)
        missing_obligation["candidates"][0]["anti_template_evaluation"][
            "obligation_ids"
        ] = []
        self.assertIn(
            "candidate color-1 must reference the category obligation",
            discovery_validator.validate(missing_obligation, "category"),
        )

        invalid_relationship = copy.deepcopy(report)
        invalid_relationship["candidates"][0]["anti_template_evaluation"][
            "relationship"
        ] = "decorates"
        self.assertIn(
            "candidate color-1 has invalid anti-template relationship",
            discovery_validator.validate(invalid_relationship, "category"),
        )

    def test_aggregate_requires_one_anti_template_baseline(self) -> None:
        anti_template = search.build_anti_template_baseline(
            _content_map(), _baseline()
        )
        reports: dict[str, object] = {}
        for category in search.CATEGORY_DOMAINS:
            with patch.object(
                search,
                "_category_candidates",
                return_value=[_candidate(category, 1), _candidate(category, 2)],
            ):
                reports[category] = search.search_category(
                    category, _content_map(), _baseline(), anti_template, {}
                )

        aggregate = search.aggregate_discovery(
            _content_map(),
            _baseline(),
            anti_template,
            reports,
            _approved_design_spec(),
        )
        self.assertEqual(aggregate["anti_template_baseline"], anti_template)
        self.assertIs(aggregate["anti_template_resolution_required"], True)

        mismatched = copy.deepcopy(reports)
        mismatched["secondary_motion"]["anti_template_baseline_id"] = (
            "anti-template-baseline:other"
        )
        with self.assertRaisesRegex(ValueError, "anti-template baseline mismatch"):
            search.aggregate_discovery(
                _content_map(),
                _baseline(),
                anti_template,
                mismatched,
                _approved_design_spec(),
            )

    def test_skill_generates_anti_template_baseline_before_structure(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").replace(
            "\r\n", "\n"
        )
        creative_contract = (
            SKILL_ROOT / "references" / "creative-direction-contract.md"
        ).read_text(encoding="utf-8")

        self.assertLess(
            skill.index("anti_template_baseline_generating"),
            skill.index("portfolio_design_search.py\" recommend"),
        )
        self.assertIn(
            'anti-template-baseline.json" `\n  --expected-type anti_template_baseline',
            skill,
        )
        self.assertGreaterEqual(skill.count("--anti-template-baseline"), 6)
        self.assertIn("provisional_unapproved", creative_contract)
        self.assertIn(
            "The provisional baseline is not approval", skill
        )
        self.assertIn(
            "Structure selection itself remains an internal Agent decision", skill
        )

    def test_creative_direction_requires_resolved_anti_template_rules(self) -> None:
        report = _creative_direction()
        expected_rules = {"anti-template.no-equal-card-grid"}
        self.assertEqual(
            creative_validator.validate(report, expected_rule_ids=expected_rules), []
        )

        missing = copy.deepcopy(report)
        del missing["anti_template_resolutions"]
        self.assertIn(
            "missing root fields: anti_template_resolutions",
            creative_validator.validate(missing, expected_rule_ids=expected_rules),
        )

        invalid = copy.deepcopy(report)
        invalid["anti_template_resolutions"][0]["status"] = "unreviewed"
        self.assertIn(
            "anti_template_resolutions[0] has invalid status",
            creative_validator.validate(invalid, expected_rule_ids=expected_rules),
        )

        incomplete = copy.deepcopy(report)
        self.assertIn(
            "anti-template resolutions do not match provisional rules",
            creative_validator.validate(
                incomplete,
                expected_rule_ids={
                    "anti-template.no-equal-card-grid",
                    "anti-template.signature-remains-visible",
                },
            ),
        )


if __name__ == "__main__":
    unittest.main()
