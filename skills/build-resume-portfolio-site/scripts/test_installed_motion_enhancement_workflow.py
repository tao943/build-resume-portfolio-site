from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class InstalledMotionEnhancementWorkflowTests(unittest.TestCase):
    def test_optional_motion_and_video_continuations_add_no_confirmation_gate(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        required = (
            "## Stage 5: Add the optional recipe-based motion layer",
            "motion_enhancement_selecting",
            "motion_poster_generating",
            "ordinary feedback",
            "motion_enhancement_generating",
            "motion_waiting_confirmation",
            "video_upgrade_available",
            "versions\\v5-motion-enhanced-poster",
            "## Stage 6: Upgrade a confirmed Poster to video",
            "video_upgrade_validating",
            "atomically",
            "versions\\v6-video-upgrade",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        for retired in (
            "motion_poster_waiting_confirmation",
            "motion_enhancement_waiting_confirmation",
            "video_upgrade_waiting_confirmation",
            "confirmations.motion_enhancement",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, text)

    def test_stage_four_prompt_keeps_the_production_hardening_baseline(self) -> None:
        prompt_path = SKILL_ROOT / "prompts" / "06-add-motion.md"
        text = prompt_path.read_text(encoding="utf-8")
        for marker in (
            "confirmed media direction/report/refined audit",
            "installed effect sources",
            "no numeric effect cap",
            "v4-motion",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

        self.assertNotIn("resource_status: awaiting-user-supplied-content", text)


if __name__ == "__main__":
    unittest.main()
