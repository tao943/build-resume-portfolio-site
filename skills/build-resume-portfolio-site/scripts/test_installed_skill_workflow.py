from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = SKILL_ROOT / "references" / "workflow-contract.md"
ARTIFACT_LAYOUT_PATH = SKILL_ROOT / "references" / "artifact-layout.md"


class InstalledSkillWorkflowTests(unittest.TestCase):
    def test_workflow_uses_one_integrated_react_vite_project(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        required = (
            "React + Vite",
            "references/react-vite-output-contract.md",
            "scripts\\validate_vite_project.py",
            ".resume-site-work\\site",
            "npm run build",
            "versions/v1-integrated",
            "one integrated website",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertNotIn("html-output-contract.md", text)
        self.assertNotIn("validate_site.py", text)
        self.assertNotIn("site-v1-prototype.html", text)

    def test_workflow_replaces_staged_confirmation_with_upfront_approval(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "schema-version-3",
            "site-todo-plan.md",
            "explicit TODO plan approval",
            "one integrated website",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        for retired in (
            "### Prototype confirmation gate",
            "### Media direction confirmation gate",
            "### Motion confirmation gate",
        ):
            self.assertNotIn(retired, text)

    def test_workflow_records_all_six_decisions_before_generation(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "overall structure",
            "typography",
            "color system",
            "conditional media treatment",
            "primary motion",
            "secondary motion",
            "independent display-only",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertNotIn("media_direction_waiting_confirmation", text)

    def test_final_acceptance_has_exactly_three_outcomes(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        layout = ARTIFACT_LAYOUT_PATH.read_text(encoding="utf-8")
        combined = skill + workflow + layout

        for outcome in ("当前效果满意，完成", "加强动效", "提出修改"):
            self.assertIn(outcome, combined)
        self.assertIn("motion_enhancing", workflow)
        self.assertNotIn("motion_waiting_confirmation", workflow)

    def test_workflow_requires_an_explicit_two_choice_strategy_gate(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "当前会话单 Agent",
            "多 Agent 并行",
            "implementation_strategy_waiting_confirmation",
            "请明确选择 1 或 2",
        ):
            self.assertIn(marker, text)
        self.assertNotIn("fresh-agent-sequential", text)


if __name__ == "__main__":
    unittest.main()
