from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class APIHzWorkflowTests(unittest.TestCase):
    def test_skill_exposes_explicit_optional_media_search_branch(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        required = (
            "APIHZ_ID",
            "APIHZ_KEY",
            "apihz_media.py\" search",
            "import_media_selection.py",
            ".resume-site-work\\media-search",
            "preview.html",
            "explicit user request",
            "GIF",
            "rights-unverified",
            "selected-only import",
            "provider-failure isolation",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, skill)

    def test_optional_prompt_enforces_preview_selection_and_local_paths(self) -> None:
        prompt = (SKILL_ROOT / "prompts" / "11-search-optional-media.md").read_text(
            encoding="utf-8"
        )
        required = (
            "resource_id: search-optional-media",
            "resource_version: 1",
            "animated GIF",
            "publication rights not verified",
            "wait for explicit candidate IDs",
            "/assets/external/",
            "Never hotlink",
            "does not dictate the site's visual language",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, prompt)

    def test_artifact_and_workflow_contracts_keep_provider_non_blocking(self) -> None:
        artifact = (SKILL_ROOT / "references" / "artifact-layout.md").read_text(
            encoding="utf-8"
        )
        workflow = (SKILL_ROOT / "references" / "workflow-contract.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("media-search/", artifact)
        self.assertIn("media-selection.json", artifact)
        self.assertIn("optional APIHz media transaction", workflow)
        self.assertIn("does not change the current portfolio stage", workflow)
        self.assertIn("normal workflow remains available", workflow)
        self.assertNotIn("<prototype|style|screenshot|motion|apihz>", skill_text())


def skill_text() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
