"""Contract checks for dynamic media visual-audit workflow resources."""

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = SKILL_ROOT / "prompts" / "04-audit-screenshot.md"
RULES_PATH = SKILL_ROOT / "references" / "screenshot-review-rules.md"
SKILL_PATH = SKILL_ROOT / "SKILL.md"


class MediaVisualAuditWorkflowTests(unittest.TestCase):
    def test_audit_prompt_records_dynamic_state_evidence_without_a_gate(self):
        prompt = PROMPT_PATH.read_text(encoding="utf-8")

        for marker in (
            "reports/visual-audit.json",
            "interaction_states_checked",
            "initial state",
            "representative active state",
            "controller family",
            "coarse-pointer",
            "reduced-motion",
            "media loading",
            "media error",
            "Poster fallback",
            "last-valid-preview",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, prompt)

        self.assertNotIn("confirmation gate", prompt.lower())

    def test_review_rules_make_dynamic_media_failures_blocking(self):
        rules = RULES_PATH.read_text(encoding="utf-8")

        for marker in (
            "clipping",
            "focus order",
            "readability",
            "image/UI cohesion",
            "controller conflicts",
            "essential-content loss",
            "scroll traps",
            "factual-media distortion",
            "absent fallbacks",
            "blocking",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, rules)

    def test_skill_runs_the_dynamic_audit_in_the_existing_two_round_flow(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")

        for marker in (
            "interaction_states_checked",
            "coarse-pointer/touch",
            "reduced-motion",
            "loading, error, and Poster fallback",
            "last valid preview",
            "visual_repair_round < 2",
            "Do not request routine confirmation",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, skill)


if __name__ == "__main__":
    unittest.main()
