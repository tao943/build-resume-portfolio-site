from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from validate_skill_resources import parse_prompt_header, validate_resources


class InstalledMediaDirectionPromptTests(unittest.TestCase):
    def test_media_direction_prompts_are_ready_with_expected_contracts(self) -> None:
        expected = {
            "02-analyze-reference.md": ("analyze-reference", "style-brief-json"),
            "03-direct-media-art.md": (
                "direct-media-art",
                "react-vite-project-update-and-media-art-direction-json",
            ),
        }

        for filename, (resource_id, output_contract) in expected.items():
            with self.subTest(filename=filename):
                metadata = parse_prompt_header(SKILL_ROOT / "prompts" / filename)
                self.assertEqual(metadata["resource_id"], resource_id)
                self.assertGreaterEqual(metadata["resource_version"], 1)
                self.assertEqual(metadata["resource_status"], "ready")
                self.assertEqual(metadata["output_contract"], output_contract)

    def test_reference_analysis_prompt_produces_transferable_style_brief(self) -> None:
        text = (SKILL_ROOT / "prompts" / "02-analyze-reference.md").read_text(
            encoding="utf-8"
        )
        required = (
            "visible evidence",
            "color_relationships",
            "typography",
            "grid_and_composition",
            "decorative_language",
            "avoid_literal_copying",
            "Return only valid JSON",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_media_direction_preserves_user_media_and_implements_one_winner(self) -> None:
        text = (SKILL_ROOT / "prompts" / "03-direct-media-art.md").read_text(
            encoding="utf-8"
        )
        required = (
            "user-provided media",
            "factual meaning",
            "internal directions",
            "one best candidate",
            "reports/media-art-direction.json",
            "same React + Vite project",
            "no numeric effect cap",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_runtime_media_direction_validation_is_ready_for_indexed_workspace(self) -> None:
        report = validate_resources(
            SKILL_ROOT,
            "runtime",
            "media-direction",
            Path(r"D:\resume"),
        )
        self.assertTrue(report.ok)
        self.assertTrue(report.ready)
        self.assertEqual(report.errors, ())


if __name__ == "__main__":
    unittest.main()
