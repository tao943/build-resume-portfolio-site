from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class InstalledMotionWorkflowTests(unittest.TestCase):
    def test_motion_prompt_is_ready_and_plans_production_hardening(self) -> None:
        text = (SKILL_ROOT / "prompts" / "06-add-motion.md").read_text(encoding="utf-8")
        required = (
            "resource_version: 1",
            "resource_status: ready",
            "confirmed media direction/report/refined audit",
            "installed effect sources",
            "reports/motion-plan.json",
            "prefers-reduced-motion",
            "no numeric effect cap",
            "v4-motion",
            "same React + Vite project",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_motion_production_contract_is_uncapped_and_keeps_sources_local(self) -> None:
        text = (SKILL_ROOT / "references" / "motion-production-contract.md").read_text(encoding="utf-8")
        required = (
            "no numeric effect cap",
            "source code",
            "reduced-motion",
            "mobile",
            "motion-plan.json",
            "MotionSite",
            "React Bits is conditional",
            "v4-motion",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertFalse((SKILL_ROOT / "references" / "react-bits-motion-contract.md").exists())
        self.assertNotIn("maximum of 3", text)

    def test_skill_registers_motion_production_before_enhancement(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        required = (
            "references/motion-production-contract.md",
            "primary-motion system",
            "compatible secondary effects",
            "numeric effect cap",
            "motion_enhancing",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

if __name__ == "__main__":
    unittest.main()
