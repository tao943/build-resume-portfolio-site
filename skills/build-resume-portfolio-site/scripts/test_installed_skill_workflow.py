from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = SKILL_ROOT / "references" / "workflow-contract.md"
ARTIFACT_LAYOUT_PATH = SKILL_ROOT / "references" / "artifact-layout.md"


class InstalledSkillWorkflowTests(unittest.TestCase):
    def test_workflow_uses_one_react_vite_project(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        required = (
            "React + Vite",
            "references/react-vite-output-contract.md",
            "scripts\\validate_vite_project.py",
            "scripts\\snapshot_vite_project.py",
            ".resume-site-work\\site",
            "npm run build",
            ".resume-site-work\\preview\\dist\\index.html",
            "versions\\v1-prototype",
            "versions\\v2-media-direction",
            "versions\\v3-refined",
            "versions\\v4-motion",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertNotIn("html-output-contract.md", text)
        self.assertNotIn("validate_site.py", text)
        self.assertNotIn("site-v1-prototype.html", text)

    def test_workflow_preserves_all_three_confirmation_gates(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for heading in (
            "### Prototype confirmation gate",
            "### Media direction confirmation gate",
            "### Motion confirmation gate",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, text)
        self.assertNotIn("### Style confirmation gate", text)
        self.assertEqual(
            [
                line
                for line in text.splitlines()
                if line.startswith("### ") and line.endswith("confirmation gate")
            ],
            [
                "### Prototype confirmation gate",
                "### Media direction confirmation gate",
                "### Motion confirmation gate",
            ],
        )

    def test_workflow_replaces_style_state_with_media_direction_state(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "media_direction_generating",
            "media_direction_waiting_confirmation",
            "confirmations.media_direction",
            "selected_media_direction_id",
            "attempted_media_direction_ids",
            "versions\\v2-media-direction",
            "reports/media-art-direction.json",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertNotIn("style_waiting_confirmation", text)

    def test_optional_motion_continuation_uses_only_the_motion_confirmation(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        layout = ARTIFACT_LAYOUT_PATH.read_text(encoding="utf-8")
        combined = skill + workflow + layout

        self.assertIn(
            "motion_waiting_confirmation --enhance--> motion_enhancement_selecting",
            workflow,
        )
        self.assertIn(
            "motion_enhancement_generating -> motion_waiting_confirmation",
            workflow,
        )
        self.assertIn('"confirmations": {"prototype": false, "media_direction": false, "motion": false}', combined)
        for retired in (
            "motion_poster_waiting_confirmation",
            "motion_enhancement_waiting_confirmation",
            "video_upgrade_waiting_confirmation",
            "confirmations.motion_enhancement",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, combined)


if __name__ == "__main__":
    unittest.main()
