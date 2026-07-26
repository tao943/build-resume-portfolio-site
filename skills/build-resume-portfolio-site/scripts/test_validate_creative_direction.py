from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_creative_direction.py"


def valid_report() -> dict:
    return {
        "schema_version": 1,
        "creative_thesis": "A calm editorial portfolio that reveals playful energy through interaction.",
        "experience_priority": [
            "Establish one memorable visual protagonist.",
            "Make project evidence easy to inspect.",
            "End with a clear growth statement.",
        ],
        "creative_freedom": {
            "fixed": [
                "Preserve all verified portfolio facts.",
                "Keep twelve projects individually reachable.",
            ],
            "open": {
                "composition": ["Explore asymmetry and controlled scale contrast."],
                "layout_patterns": ["Compare Kinetic Marquee, Horizontal Pan, and Sticky Stack."],
                "motion_language": ["Use motion to reveal hierarchy, not decorate every element."],
                "visual_metaphor": ["Explore broadcast, archive, or stage metaphors."],
                "surface_treatment": ["Explore grain, light, and editorial rules."],
            },
            "avoid": [
                "Generic equal-card grid.",
                "Motion that obscures project text.",
            ],
        },
        "layout_candidates": [
            {
                "id": "kinetic-archive",
                "family": "Kinetic Marquee",
                "fit": "Turns the project collection into a continuous broadcast.",
                "risks": ["Can compete with reading if speed is too high."],
                "responsive_fallback": "Use a swipeable linear rail on coarse pointers.",
            },
            {
                "id": "editorial-stack",
                "family": "Sticky Stack",
                "fit": "Builds a clear narrative from introduction to evidence.",
                "risks": ["Needs careful section-height tuning."],
                "responsive_fallback": "Use normal document flow on narrow screens.",
            },
        ],
        "selected_candidate_id": "kinetic-archive",
        "selection_rationale": "It best supports the approved broadcast metaphor while keeping each project reachable.",
        "concept_prototype": {
            "visual_protagonist": "One expressive character-led hero establishes the first viewport.",
            "composition_commitment": "The selected kinetic archive family shapes the project section immediately.",
            "type_color_character": "Editorial display type and warm luminous contrast create an initial personality.",
            "representative_interaction_state": "Show one project rail item in its active, expanded state.",
            "template_independence_test": "Without final media or motion, scale, rhythm, and asymmetry still identify the page.",
            "deferred_to_later": [
                "Reference-derived surface finishing.",
                "Production motion timing and cleanup.",
                "Final media crops and compression.",
            ],
        },
        "responsive_freedom": {
            "must_preserve": ["Project identity and keyboard access."],
            "may_adapt": ["Motion density, crop, ordering, and layout family expression."],
        },
        "motion_freedom": {
            "purpose": "Support hierarchy and narrative progression.",
            "allowed": ["Continuous low-speed movement", "direct-manipulation feedback"],
            "avoid": ["scroll traps", "essential content available only through motion"],
        },
        "review_questions": [
            "Is the visual protagonist clear in the first viewport?",
            "Can every project be reached with keyboard and touch?",
            "Does reduced motion preserve the narrative hierarchy?",
        ],
    }


class CreativeDirectionValidatorTests(unittest.TestCase):
    def run_validator(self, report: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "creative-direction.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_an_open_ended_creative_direction(self) -> None:
        result = self.run_validator(valid_report())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_overlap_between_fixed_open_and_avoid(self) -> None:
        report = valid_report()
        report["creative_freedom"]["avoid"].append(
            "Preserve all verified portfolio facts."
        )
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("freedom overlap", result.stdout)

    def test_rejects_a_missing_selected_candidate(self) -> None:
        report = valid_report()
        report["selected_candidate_id"] = "unknown"
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("selected_candidate_id", result.stdout)

    def test_rejects_insufficient_layout_family_diversity(self) -> None:
        report = valid_report()
        report["layout_candidates"][1]["family"] = "Kinetic Marquee"
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("distinct layout families", result.stdout)

    def test_rejects_source_or_component_tree_payloads(self) -> None:
        report = valid_report()
        report["creative_thesis"] = "<section><ProjectGrid /></section>"
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("implementation payload", result.stdout)

    def test_rejects_pixel_prescriptions_in_open_space(self) -> None:
        report = valid_report()
        report["creative_freedom"]["open"]["composition"] = [
            "Use a 320px card in a 3-column grid."
        ]
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("pixel-level prescription", result.stdout)

    def test_rejects_a_missing_concept_prototype(self) -> None:
        report = valid_report()
        del report["concept_prototype"]
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("concept_prototype", result.stdout)

    def test_rejects_deferring_first_version_visual_commitments(self) -> None:
        report = valid_report()
        report["concept_prototype"]["deferred_to_later"].append(
            "Selected layout family and initial visual hierarchy."
        )
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot defer first-version visual commitments", result.stdout)


if __name__ == "__main__":
    unittest.main()
