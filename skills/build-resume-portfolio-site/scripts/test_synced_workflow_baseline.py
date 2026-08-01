from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SyncedWorkflowBaselineTests(unittest.TestCase):
    def test_required_newer_baseline_resources_exist(self) -> None:
        required = [
            "references/content-preflight-routing-contract.md",
            "references/creative-direction-contract.md",
            "references/creative-direction-schema.json",
            "references/multi-agent-implementation-contract.md",
            "references/multi-agent-implementation-schema.json",
            "scripts/validate_content_handoff.py",
            "scripts/validate_creative_direction.py",
            "scripts/validate_multi_agent_plan.py",
        ]
        missing = [path for path in required if not (ROOT / path).is_file()]
        self.assertEqual(missing, [])

    def test_skill_routes_content_and_selects_agent_strategy(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("resume-content-intelligence", text)
        self.assertIn("当前会话单 Agent", text)
        self.assertIn("多 Agent 并行", text)
        self.assertNotIn("fresh-agent-sequential", text)
        self.assertIn("parallel-wave", text)
        self.assertIn("creative-direction.json", text)

    def test_skill_uses_upfront_design_and_todo_approval(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "schema-version-3",
            "site-todo-plan.md",
            "one integrated website",
            "当前效果满意，完成",
            "加强动效",
            "提出修改",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
