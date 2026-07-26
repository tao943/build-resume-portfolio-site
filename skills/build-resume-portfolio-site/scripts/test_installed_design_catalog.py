from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SOURCE_SKILL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SOURCE_SKILL_ROOT.parents[1]
INSTALLED_SKILL_ROOT = SOURCE_SKILL_ROOT
PLUGIN_MANIFEST = REPOSITORY_ROOT / ".codex-plugin" / "plugin.json"


class InstalledDesignCatalogTests(unittest.TestCase):
    def test_plugin_metadata_advertises_offline_design_intelligence(self) -> None:
        manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "1.2.0")
        self.assertIn("design-intelligence", manifest["keywords"])
        self.assertIn("offline-catalog", manifest["keywords"])

    def test_installed_skill_contains_vendor_license_and_runtime_resources(self) -> None:
        required = (
            "vendor/ui-ux-pro-max/LICENSE",
            "vendor/ui-ux-pro-max/MANIFEST.sha256",
            "vendor/ui-ux-pro-max/data/styles.csv",
            "vendor/ui-ux-pro-max/data/stacks/react.csv",
            "scripts/portfolio_design_search.py",
            "scripts/validate_design_catalog.py",
            "references/design-intelligence-contract.md",
            "references/design-intelligence-schema.json",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((INSTALLED_SKILL_ROOT / relative).is_file(), relative)

    def test_installed_search_runs_without_importing_external_ui_ux_skill(self) -> None:
        script = INSTALLED_SKILL_ROOT / "scripts" / "portfolio_design_search.py"
        self.assertTrue(script.is_file(), script)
        scripts_dir = str(script.parent)
        sys.path.insert(0, scripts_dir)
        try:
            spec = importlib.util.spec_from_file_location("installed_portfolio_design_search", script)
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader if spec else None)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            result = module.recommend(
                {
                    "profile": {"role": "frontend engineer", "industry": "technology"},
                    "projects": [{"domain": "developer tools", "technologies": ["React"]}],
                    "skills": ["React", "accessibility"],
                    "media": {"project_images": 1},
                }
            )
        finally:
            sys.path.remove(scripts_dir)
        self.assertEqual(len(result["candidate_directions"]), 3)
        self.assertEqual(result["provenance"]["catalog_version"], "2.11.0")


if __name__ == "__main__":
    unittest.main()
