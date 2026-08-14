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
            "prompts/extract-content-facts.md",
            "prompts/ask-content-clarification.md",
            "prompts/optimize-content-copy.md",
            "references/content-package-contract.md",
            "references/jd-customization-rules.md",
            "references/jd-match-schema.json",
            "scripts/validate_content_package.py",
            "scripts/validate_content_design_spec.py",
            "scripts/validate_content_implementation_plan.py",
            "scripts/validate_jd_match.py",
            "scripts/write_resume_site_input.py",
        ]
        missing = [path for path in required if not (ROOT / path).is_file()]
        self.assertEqual(missing, [])

    def test_skill_routes_content_and_selects_agent_strategy(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("bundled content workflow", text)
        self.assertNotIn("resume-content-intelligence", text)
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

    def test_skill_uses_database_first_inherited_design_discovery(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn('portfolio_design_search.py" baseline', text)
        for category in (
            "structure",
            "typography",
            "color",
            "media",
            "primary_motion",
            "secondary_motion",
        ):
            self.assertIn(f"--category {category}", text)
        self.assertIn("inherited_decision_ids", text)


if __name__ == "__main__":
    unittest.main()
