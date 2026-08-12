from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class CompetitionReleaseSafetyTests(unittest.TestCase):
    def test_platform_branding_and_platform_specific_configuration_are_not_bundled(self) -> None:
        removed_paths = (
            "agents/openai.yaml",
            "scripts/configure_codex_shadcn_mcp.py",
            "scripts/test_configure_codex_shadcn_mcp.py",
        )
        for relative in removed_paths:
            with self.subTest(relative=relative):
                self.assertFalse((SKILL_ROOT / relative).exists())

        forbidden = ("codex", "openai", "chatgpt", "gpt")
        referenced_by: list[str] = []
        for path in SKILL_ROOT.rglob("*"):
            if not path.is_file() or path.name.startswith("test_"):
                continue
            try:
                text = path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                continue
            if any(marker in text for marker in forbidden):
                referenced_by.append(path.relative_to(SKILL_ROOT).as_posix())
        self.assertEqual(referenced_by, [])

    def test_external_content_skill_is_not_required_or_referenced(self) -> None:
        forbidden = ("resume-content-intelligence", "required sub-skill")
        referenced_by: list[str] = []
        for path in SKILL_ROOT.rglob("*"):
            if not path.is_file() or path.name.startswith("test_"):
                continue
            try:
                text = path.read_text(encoding="utf-8").lower()
            except UnicodeDecodeError:
                continue
            if any(marker in text for marker in forbidden):
                referenced_by.append(path.relative_to(SKILL_ROOT).as_posix())
        self.assertEqual(referenced_by, [])

    def test_remote_react_bits_registry_is_not_bundled_or_referenced(self) -> None:
        self.assertFalse((SKILL_ROOT / "scripts" / "ensure_react_bits_registry.py").exists())
        self.assertFalse((SKILL_ROOT / "scripts" / "test_ensure_react_bits_registry.py").exists())

        referenced_by: list[str] = []
        for folder in ("prompts", "references"):
            for path in (SKILL_ROOT / folder).rglob("*.md"):
                text = path.read_text(encoding="utf-8")
                if "ensure_react_bits_registry" in text or "reactbits.dev/r/" in text:
                    referenced_by.append(path.relative_to(SKILL_ROOT).as_posix())
        self.assertEqual(referenced_by, [])

    def test_raw_motion_prompt_sources_are_not_bundled(self) -> None:
        sources = SKILL_ROOT / "assets" / "motion-enhancement" / "sources"
        self.assertFalse(sources.exists())

    def test_structured_motion_recipe_system_is_not_bundled_or_referenced(self) -> None:
        removed_paths = (
            "assets/motion-enhancement/catalog",
            "prompts/07-select-motion-enhancement.md",
            "prompts/08-plan-motion-media.md",
            "prompts/09-apply-motion-enhancement.md",
            "references/motion-enhancement-contract.md",
            "references/motion-recipe-schema.md",
            "scripts/validate_motion_catalog.py",
            "scripts/test_validate_motion_catalog.py",
            "scripts/validate_motion_plan.py",
            "scripts/test_validate_motion_plan.py",
        )
        for relative in removed_paths:
            with self.subTest(relative=relative):
                self.assertFalse((SKILL_ROOT / relative).exists())

        forbidden = (
            "motion-catalog",
            "select-motion-enhancement",
            "plan-motion-media",
            "apply-motion-enhancement",
            "motion-recipe-schema",
        )
        referenced_by: list[str] = []
        for folder in ("prompts", "references", "scripts"):
            for path in (SKILL_ROOT / folder).rglob("*"):
                if not path.is_file() or path.name == Path(__file__).name:
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                if any(marker in text for marker in forbidden):
                    referenced_by.append(path.relative_to(SKILL_ROOT).as_posix())
        self.assertEqual(referenced_by, [])


if __name__ == "__main__":
    unittest.main()
