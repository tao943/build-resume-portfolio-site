from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class WorkflowBehaviorContractTests(unittest.TestCase):
    def read_skill(self, name: str) -> str:
        return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")

    def read_site_reference(self, name: str) -> str:
        return (
            ROOT
            / "skills"
            / "build-resume-portfolio-site"
            / "references"
            / name
        ).read_text(encoding="utf-8")

    def run_validator(
        self,
        skill: str,
        script: str,
        fixture: str,
        mutate=None,
    ) -> subprocess.CompletedProcess[str]:
        payload = json.loads((FIXTURES / fixture).read_text(encoding="utf-8"))
        if mutate is not None:
            mutate(payload)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / fixture
            path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "skills" / skill / "scripts" / script),
                    str(path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_all_three_skills_are_discoverable(self) -> None:
        for name in (
            "resume-portfolio-workflow",
            "resume-content-intelligence",
            "build-resume-portfolio-site",
        ):
            self.assertTrue((ROOT / "skills" / name / "SKILL.md").is_file())

    def test_visual_companion_is_packaged_with_website_skill(self) -> None:
        root = ROOT / "skills" / "build-resume-portfolio-site"
        for relative in (
            "assets/visual-companion/gallery-shell.html",
            "references/visual-style-preview-contract.md",
            "scripts/visual_companion/server.cjs",
            "scripts/visual_companion/launch.cjs",
            "scripts/visual_companion/stop.cjs",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((root / relative).is_file(), relative)

    def test_domain_skills_internalize_discovery_and_planning(self) -> None:
        for name in ("resume-content-intelligence", "build-resume-portfolio-site"):
            text = self.read_skill(name)
            self.assertIn("one question at a time", text.lower())
            self.assertIn("implementation plan", text.lower())
            self.assertNotIn("required sub-skill: use superpowers:", text.lower())

    def test_site_skill_blocks_source_edits_before_approval(self) -> None:
        text = self.read_skill("build-resume-portfolio-site")
        self.assertIn("Do not edit React source before", text)
        self.assertIn("site-design-spec.json", text)

    def test_site_discovery_requires_display_only_visual_gallery(self) -> None:
        text = self.read_skill("build-resume-portfolio-site").lower()
        self.assertIn("visual-style-preview-contract.md", text)
        self.assertIn("approval remains in the conversation", text)
        self.assertIn("launch.cjs", text)
        self.assertIn("complete authenticated url", text)
        self.assertIn("static html fallback", text)
        self.assertIn("do not edit react source", text)

    def test_browser_activity_never_counts_as_approval(self) -> None:
        contract = (
            ROOT
            / "skills"
            / "build-resume-portfolio-site"
            / "references"
            / "site-brainstorming-contract.md"
        ).read_text(encoding="utf-8").lower()
        self.assertIn("browser activity never counts as approval", contract)
        self.assertIn("two or three", contract)
        self.assertIn("gallery.html", contract)

    def test_artifact_layout_owns_style_preview_sessions(self) -> None:
        layout = (
            ROOT
            / "skills"
            / "build-resume-portfolio-site"
            / "references"
            / "artifact-layout.md"
        ).read_text(encoding="utf-8").lower()
        self.assertIn("style-preview", layout)
        self.assertIn("discovery evidence", layout)
        self.assertIn("not react source", layout)

    def test_full_discovery_orders_six_independent_decisions(self) -> None:
        contract = self.read_site_reference(
            "site-brainstorming-contract.md"
        ).lower()
        markers = (
            "overall structure",
            "typography",
            "color system",
            "media treatment",
            "primary motion",
            "secondary motion",
            "final requirements confirmation",
            "todo plan approval",
        )
        positions = [contract.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_each_enabled_decision_gets_a_separate_preview_offer(self) -> None:
        contract = self.read_site_reference(
            "visual-style-preview-contract.md"
        ).lower()
        self.assertIn("ask separately for every enabled category", contract)
        self.assertIn("independent, not cumulative", contract)
        self.assertIn("declining one category", contract)

    def test_site_skill_requires_readable_plan_approval_before_source_edits(
        self,
    ) -> None:
        text = self.read_skill("build-resume-portfolio-site").lower()
        self.assertIn("site-todo-plan.md", text)
        self.assertIn("todo plan approval", text)
        self.assertIn("do not edit react source", text)
        self.assertIn("one integrated", text)

    def test_final_acceptance_has_three_explicit_outcomes(self) -> None:
        skill = self.read_skill("build-resume-portfolio-site")
        for choice in (
            "当前效果满意，完成",
            "加强动效",
            "提出修改",
        ):
            self.assertIn(choice, skill)
        workflow = self.read_site_reference("workflow-contract.md").lower()
        for preserved in (
            "structure",
            "typography",
            "color",
            "media treatment",
        ):
            self.assertIn(preserved, workflow)

    def test_readme_documents_cross_agent_visual_preview(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("visual companion", readme)
        self.assertIn("codex", readme)
        self.assertIn("claude code", readme)
        self.assertIn("cursor", readme)
        self.assertIn("copilot cli", readme)
        self.assertIn("conversation", readme)

    def test_valid_full_workflow_artifacts_pass(self) -> None:
        cases = (
            (
                "resume-content-intelligence",
                "validate_content_design_spec.py",
                "content-design-spec-valid.json",
            ),
            (
                "resume-content-intelligence",
                "validate_content_implementation_plan.py",
                "content-plan-valid.json",
            ),
            (
                "build-resume-portfolio-site",
                "validate_site_design_spec.py",
                "site-design-spec-valid.json",
            ),
            (
                "build-resume-portfolio-site",
                "validate_site_implementation_plan.py",
                "site-plan-valid.json",
            ),
            (
                "resume-portfolio-workflow",
                "validate_workflow_route.py",
                "workflow-route-fast-valid.json",
            ),
        )
        for skill, script, fixture in cases:
            with self.subTest(fixture=fixture):
                result = self.run_validator(skill, script, fixture)
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_rushed_site_cannot_collapse_discovery_to_one_option(self) -> None:
        result = self.run_validator(
            "build-resume-portfolio-site",
            "validate_site_design_spec.py",
            "site-design-spec-valid.json",
            lambda payload: payload["decisions"]["structure"].update(
                {
                    "candidates": payload["decisions"]["structure"][
                        "candidates"
                    ][:1]
                }
            ),
        )
        self.assertNotEqual(result.returncode, 0)

    def test_full_site_requires_a_preview_record_per_enabled_category(self) -> None:
        result = self.run_validator(
            "build-resume-portfolio-site",
            "validate_site_design_spec.py",
            "site-design-spec-valid.json",
            lambda payload: payload["decisions"]["structure"].pop("preview"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("structure requires a preview record", result.stdout)

    def test_browser_activity_cannot_approve_site_design(self) -> None:
        result = self.run_validator(
            "build-resume-portfolio-site",
            "validate_site_design_spec.py",
            "site-design-spec-valid.json",
            lambda payload: payload["decisions"]["structure"][
                "approval"
            ].update(
                {"channel": "browser"}
            ),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "structure approval must be explicit and conversational",
            result.stdout,
        )

    def test_version_two_site_design_is_rejected(self) -> None:
        result = self.run_validator(
            "build-resume-portfolio-site",
            "validate_site_design_spec.py",
            "site-design-spec-valid.json",
            lambda payload: payload.update({"schema_version": 2}),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("schema_version must be 3", result.stdout)

    def test_unsupported_claim_cannot_enter_content_plan(self) -> None:
        def remove_evidence(payload: dict) -> None:
            task = payload["tasks"][0]
            task["fact_ids"] = []
            task["evidence_ids"] = []
            task["blocked_claims"] = []

        result = self.run_validator(
            "resume-content-intelligence",
            "validate_content_implementation_plan.py",
            "content-plan-valid.json",
            remove_evidence,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_overlapping_parallel_ownership_is_rejected(self) -> None:
        def overlap(payload: dict) -> None:
            payload["strategy"] = "parallel-wave"
            payload["multi_agent_authorized"] = True
            payload["multi_agent_plan"] = "reports/multi-agent-plan.json"
            duplicate = dict(payload["tasks"][0])
            duplicate["id"] = "duplicate-owner"
            payload["tasks"].append(duplicate)

        result = self.run_validator(
            "build-resume-portfolio-site",
            "validate_site_implementation_plan.py",
            "site-plan-valid.json",
            overlap,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_fast_change_rejects_structural_scope(self) -> None:
        result = self.run_validator(
            "resume-portfolio-workflow",
            "validate_workflow_route.py",
            "workflow-route-fast-valid.json",
            lambda payload: payload.update({"structural_scope_changed": True}),
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
