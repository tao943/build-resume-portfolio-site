from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StructureSeedWorkflowTests(unittest.TestCase):
    def test_skill_uses_agent_owned_three_direction_flow(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "references/structure-seed-contract.md",
            "references/visual-fingerprint-contract.md",
            "`fit`,",
            "`novelty`, and `wildcard`",
            "script_recommended_direction_id",
            "Do not expose the internal candidates as a new user gate",
            "schema-version-4",
        ):
            self.assertIn(phrase, text)

    def test_motion_and_audit_are_separate_from_seed(self) -> None:
        motion = (ROOT / "references" / "motion-production-contract.md").read_text(encoding="utf-8")
        audit = (ROOT / "references" / "screenshot-review-rules.md").read_text(encoding="utf-8")
        self.assertIn("winning static composition before motion planning", motion)
        self.assertIn("never generic background particles", motion)
        self.assertIn("four layers", audit)
        self.assertIn("palette or font swap is not structural novelty", audit)

    def test_catalog_does_not_lock_visual_styling(self) -> None:
        contract = (ROOT / "references" / "structure-seed-contract.md").read_text(encoding="utf-8")
        self.assertIn("not a template", contract)
        self.assertIn("must not contain", contract)
        self.assertIn("fonts", contract)


if __name__ == "__main__":
    unittest.main()
