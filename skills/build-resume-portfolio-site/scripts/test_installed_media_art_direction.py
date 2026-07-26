"""Verify the packaged media-art-direction Skill is installed completely."""

from __future__ import annotations

import json
import hashlib
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
PLUGIN_MANIFEST = (
    REPOSITORY_ROOT
    / ".codex-plugin"
    / "plugin.json"
)
INSTALLED_SKILL = SKILL_ROOT
SYNC_EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "node_modules",
        "dist",
        "tmp",
        "temp",
        ".resume-site-work",
    }
)


def included_file_inventory(root: Path) -> dict[str, str]:
    """Return relative file hashes for exactly the files copied by the mirror."""
    inventory: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SYNC_EXCLUDED_DIRECTORIES for part in relative.parts):
            continue
        inventory[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return inventory


class InstalledMediaArtDirectionTests(unittest.TestCase):
    def test_plugin_metadata_describes_the_internal_winner_workflow(self) -> None:
        plugin = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(plugin["version"], "1.2.0")
        self.assertIn("media-art-direction", plugin["keywords"])
        description = plugin["description"].lower()
        self.assertIn("multiple", description)
        self.assertIn("one", description)
        self.assertIn("winner", description)
        self.assertNotIn("bundled production components", description)
        interface = plugin["interface"]
        long_description = interface["longDescription"].lower()
        self.assertIn("media-direction winner", long_description)
        self.assertIn("source-agnostic production-hardened motion", long_description)
        self.assertNotIn("reference styling", long_description)
        self.assertNotIn("react bits motion stages", long_description)
        prompts = " ".join(interface["defaultPrompt"]).lower()
        self.assertIn("media-direction winner", prompts)
        self.assertIn("source-agnostic production-hardened motion", prompts)

    def test_installed_runtime_contains_new_resources_and_excludes_retired_ones(self) -> None:
        expected = (
            "prompts/03-direct-media-art.md",
            "prompts/04-audit-screenshot.md",
            "references/media-art-direction-contract.md",
            "references/media-art-direction-schema.json",
            "references/motion-production-contract.md",
            "references/screenshot-review-rules.md",
            "scripts/validate_media_art_direction.py",
            "scripts/test_media_visual_audit_workflow.py",
        )
        for relative in expected:
            with self.subTest(relative=relative):
                self.assertTrue((INSTALLED_SKILL / relative).is_file(), relative)

        for relative in (
            "prompts/03-apply-style.md",
            "references/react-bits-motion-contract.md",
        ):
            with self.subTest(relative=relative):
                self.assertFalse((INSTALLED_SKILL / relative).exists(), relative)

    def test_packaged_skill_inventory_contains_current_workflow_resources(self) -> None:
        source_inventory = included_file_inventory(SKILL_ROOT)
        for relative in (
            "references/site-brainstorming-contract.md",
            "references/site-planning-contract.md",
            "scripts/migrate_build_state.py",
            "scripts/validate_site_design_spec.py",
            "scripts/validate_site_implementation_plan.py",
        ):
            with self.subTest(relative=relative):
                self.assertIn(relative, source_inventory)

    def test_inventory_detects_a_content_mismatch_in_temporary_trees(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "source"
            installed = Path(temporary_directory) / "installed"
            source.mkdir()
            installed.mkdir()
            (source / "SKILL.md").write_text("source", encoding="utf-8")
            (installed / "SKILL.md").write_text("installed", encoding="utf-8")
            (source / "__pycache__").mkdir()
            (source / "__pycache__" / "ignored.pyc").write_bytes(b"cache")

            self.assertNotEqual(
                included_file_inventory(source),
                included_file_inventory(installed),
            )


if __name__ == "__main__":
    unittest.main()
