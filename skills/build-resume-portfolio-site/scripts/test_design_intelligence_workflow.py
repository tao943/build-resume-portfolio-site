from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_skill_resources import STAGE_RESOURCES, validate_resources


class DesignIntelligenceWorkflowTests(unittest.TestCase):
    def test_prototype_and_style_require_the_vendored_design_catalog(self) -> None:
        self.assertIn("design-catalog", STAGE_RESOURCES["prototype"])
        self.assertIn("design-catalog", STAGE_RESOURCES["style"])

    def test_prototype_runs_design_search_before_react_generation(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        prompt = (SKILL_ROOT / "prompts" / "01-generate-prototype.md").read_text(
            encoding="utf-8"
        )
        for marker in (
            "scripts\\portfolio_design_search.py",
            "reports\\design-intelligence.json",
            "references/design-intelligence-contract.md",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, skill)
        self.assertIn("design-intelligence.json", prompt)
        self.assertIn("fixed component tree", prompt)
        self.assertIn("fixed JSX", prompt)

    def test_style_prompt_keeps_reference_evidence_primary(self) -> None:
        prompt = (SKILL_ROOT / "prompts" / "03-apply-style.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("design-intelligence.json", prompt)
        self.assertIn("reference evidence has priority", prompt)
        self.assertIn("Catalog", prompt)

    def test_style_runtime_allows_catalog_only_when_reference_library_is_absent(self) -> None:
        absent_workspace = SCRIPT_DIR / "workspace-without-reference-library"

        report = validate_resources(
            SKILL_ROOT, "runtime", "style", workspace_root=absent_workspace
        )

        self.assertTrue(report.ok, report.errors)
        self.assertTrue(report.ready, report.errors)
        self.assertEqual(report.errors, ())


if __name__ == "__main__":
    unittest.main()
