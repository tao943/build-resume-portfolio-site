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
            "confirmed media direction/report/refined audit",
            "no numeric effect cap",
            "motion_enhancement_selecting",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_motion_selection_prompt_accepts_multiple_recipes_without_numeric_limits(self) -> None:
        text = (SKILL_ROOT / "prompts" / "07-select-motion-enhancement.md").read_text(encoding="utf-8")
        self.assertIn("multiple primary recipes", text)
        self.assertIn("multiple secondary effects", text)
        self.assertIn("conflict_resolution", text)
        self.assertNotIn("zero or one", text)

    def test_motion_apply_prompt_applies_all_compatible_selected_items_without_caps(self) -> None:
        text = (SKILL_ROOT / "prompts" / "09-apply-motion-enhancement.md").read_text(encoding="utf-8")
        self.assertIn("all compatible selected primary recipes and secondary effects", text)
        self.assertIn("target/controller conflict_resolution", text)
        self.assertNotIn("Apply one selected primary recipe", text)
        self.assertNotIn("at most one compatible lightweight local effect", text)


if __name__ == "__main__":
    unittest.main()
