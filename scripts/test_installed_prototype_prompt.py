from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_skill_resources import parse_prompt_header, validate_resources


class InstalledPrototypePromptTests(unittest.TestCase):
    def test_prototype_resource_is_ready_for_react_vite_generation(self) -> None:
        report = validate_resources(SKILL_ROOT, "runtime", "prototype")
        self.assertTrue(report.ok)
        self.assertTrue(report.ready)
        self.assertEqual(report.errors, ())

        metadata = parse_prompt_header(SKILL_ROOT / "prompts" / "01-generate-prototype.md")
        self.assertGreaterEqual(metadata["resource_version"], 2)
        self.assertEqual(metadata["resource_status"], "ready")
        self.assertEqual(metadata["output_contract"], "react-vite-project")

    def test_prototype_prompt_covers_the_approved_brief(self) -> None:
        body = (SKILL_ROOT / "prompts" / "01-generate-prototype.md").read_text(
            encoding="utf-8"
        )
        required_terms = (
            "React",
            "Vite",
            "Hero",
            "视频",
            "个人经历",
            "精选项目",
            "个人优势",
            "联系方式",
            "1700px",
            "fallback",
            "不得编造",
            "npm run build",
        )
        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, body)


if __name__ == "__main__":
    unittest.main()
