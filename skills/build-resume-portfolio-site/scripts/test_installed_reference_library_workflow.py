from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class InstalledReferenceLibraryWorkflowTests(unittest.TestCase):
    def test_skill_documents_catalog_build_and_workspace_validation(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        required = (
            "index_reference_library.py",
            "--workspace-root",
            "reference-library",
            "contact-sheets",
            "reference-selection.json",
            "style_only",
            "absolute Markdown image paths",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_catalog_contract_is_documented(self) -> None:
        contract = (SKILL_ROOT / "references" / "reference-library-contract.md").read_text(encoding="utf-8")
        for marker in ("manifest.json", "source_path", "usage_scope", "contact-sheets", "rights not verified"):
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)


if __name__ == "__main__":
    unittest.main()
