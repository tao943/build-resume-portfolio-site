from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_skill_resources import validate_resources


SKILL_ROOT = Path(__file__).resolve().parents[1]
PROMPTS = {
    "generate-integrated-site": (
        "01-generate-integrated-site.md",
        "react-vite-integrated-site",
    ),
    "generate-prototype": ("01-generate-prototype.md", "react-vite-project"),
    "analyze-reference": ("02-analyze-reference.md", "style-brief-json"),
    "direct-media-art": (
        "03-direct-media-art.md",
        "react-vite-project-update-and-media-art-direction-json",
    ),
    "audit-screenshot": ("04-audit-screenshot.md", "visual-audit-json"),
    "repair-local-issues": ("05-repair-local-issues.md", "react-vite-project-update"),
    "add-motion": ("06-add-motion.md", "react-vite-project-update-and-motion-plan-json"),
    "upgrade-poster-to-video": (
        "10-upgrade-poster-to-video.md",
        "react-vite-media-only-update-and-video-validation-json",
    ),
}

CONTRACTS = (
    "site-brainstorming-contract.md",
    "site-design-spec-schema.json",
    "site-planning-contract.md",
    "site-implementation-plan-schema.json",
    "visual-style-preview-contract.md",
    "design-contract.md",
    "design-contract-schema.json",
    "visual-audit-schema.json",
)
VISUAL_COMPANION_FILES = (
    "assets/visual-companion/gallery-shell.html",
    "scripts/visual_companion/server.cjs",
    "scripts/visual_companion/launch.cjs",
    "scripts/visual_companion/stop.cjs",
)
AESTHETIC_QUALITY_FILES = (
    "references/creative-direction-contract.md",
    "references/creative-direction-schema.json",
    "references/design-discovery-schema.json",
    "assets/structure-seeds/catalog.json",
    "references/structure-seed-contract.md",
    "references/structure-seed-schema.json",
    "references/visual-fingerprint-contract.md",
    "references/visual-fingerprint-schema.json",
    "references/design-contract.md",
    "references/design-contract-schema.json",
    "references/visual-audit-schema.json",
    "scripts/validate_design_contract.py",
    "scripts/validate_creative_direction.py",
    "scripts/validate_design_discovery.py",
    "scripts/validate_visual_audit.py",
    "scripts/validate_structure_seeds.py",
    "scripts/structure_seed_selector.py",
    "scripts/portfolio_design_search.py",
)
CONTENT_WORKFLOW_FILES = (
    "prompts/extract-content-facts.md",
    "prompts/ask-content-clarification.md",
    "prompts/optimize-content-copy.md",
    "references/ats-safety-checklist.md",
    "references/content-brainstorming-contract.md",
    "references/content-conversation-workflow.md",
    "references/content-design-spec-schema.json",
    "references/content-implementation-plan-schema.json",
    "references/content-package-contract.md",
    "references/content-planning-contract.md",
    "references/content-quality-gate.md",
    "references/content-quality-review-schema.json",
    "references/evidence-schema.json",
    "references/fact-verification-rules.md",
    "references/jd-customization-rules.md",
    "references/jd-match-schema.json",
    "references/resume-content-schema.json",
    "references/star-and-impact-rubric.md",
    "references/writing-coach-rules.md",
    "scripts/extract_resume_text.py",
    "scripts/normalize_resume_sources.py",
    "scripts/validate_content_design_spec.py",
    "scripts/validate_content_handoff.py",
    "scripts/validate_content_implementation_plan.py",
    "scripts/validate_content_package.py",
    "scripts/validate_content_quality_review.py",
    "scripts/validate_jd_match.py",
    "scripts/write_resume_site_input.py",
)


def write_prompt(root: Path, resource_id: str, *, ready: bool = False) -> None:
    filename, output_contract = PROMPTS[resource_id]
    status = "ready" if ready else "awaiting-user-supplied-content"
    version = 1 if ready else 0
    body = (
        "Use the supplied source material and return the contracted output."
        if ready
        else f"Stop this stage and report `resource_not_ready: {resource_id}`."
    )
    prompt_dir = root / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / filename).write_text(
        "\n".join(
            [
                "---",
                f"resource_id: {resource_id}",
                f"resource_version: {version}",
                f"resource_status: {status}",
                f"output_contract: {output_contract}",
                "---",
                "",
                body,
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_manifest(root: Path, *, ready: bool = False) -> None:
    manifest_dir = root / "assets" / "reference-library"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    references = (
        [
            {
                "id": "editorial-01",
                "path": "editorial-01.png",
                "role_tags": ["designer"],
                "visual_tags": ["editorial"],
                "source_note": "user supplied",
                "license_note": "style reference only",
                "aspect_ratio": "16:10",
                "available": True,
            }
        ]
        if ready
        else []
    )
    (manifest_dir / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "library_status": "ready" if ready else "awaiting-user-supplied-content",
                "library_version": 1 if ready else 0,
                "references": references,
            }
        ),
        encoding="utf-8",
    )
    if ready:
        (manifest_dir / "editorial-01.png").write_bytes(b"reference")


def write_complete_skeleton(root: Path) -> None:
    for resource_id in PROMPTS:
        write_prompt(root, resource_id)
    write_manifest(root)
    references = root / "references"
    references.mkdir(parents=True, exist_ok=True)
    for filename in CONTRACTS:
        shutil.copy2(SKILL_ROOT / "references" / filename, references / filename)
    shutil.copytree(
        SKILL_ROOT / "vendor" / "ui-ux-pro-max",
        root / "vendor" / "ui-ux-pro-max",
    )
    for relative in VISUAL_COMPANION_FILES:
        source = SKILL_ROOT / relative
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    for relative in AESTHETIC_QUALITY_FILES:
        source = SKILL_ROOT / relative
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            shutil.copy2(source, destination)
    for relative in CONTENT_WORKFLOW_FILES:
        source = SKILL_ROOT / relative
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)




def write_workspace_manifest(root: Path) -> None:
    manifest_dir = root / ".resume-site-work" / "reference-library"
    (manifest_dir / "thumbnails").mkdir(parents=True, exist_ok=True)
    (manifest_dir / "thumbnails" / "ref-01.png").write_bytes(b"reference")
    (manifest_dir / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "library_status": "ready",
                "library_version": 1,
                "references": [
                    {
                        "id": "ref-01",
                        "path": "thumbnails/ref-01.png",
                        "role_tags": [],
                        "visual_tags": ["wide"],
                        "source_note": "user supplied",
                        "license_note": "style only",
                        "aspect_ratio": "16:10",
                        "available": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
class ValidateSkillResourcesTests(unittest.TestCase):
    def test_content_stage_accepts_complete_bundled_workflow(self) -> None:
        report = validate_resources(SKILL_ROOT, "runtime", "content-preparation")
        self.assertTrue(report.ok, report.errors)
        self.assertTrue(report.ready, report.errors)

    def test_skeleton_rejects_each_missing_content_workflow_file(self) -> None:
        for relative in CONTENT_WORKFLOW_FILES:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                write_complete_skeleton(root)
                (root / relative).unlink()
                report = validate_resources(root, "skeleton", None)
                self.assertFalse(report.ok)
                self.assertIn(
                    f"missing_content_workflow_file: {relative}", report.errors
                )

    def test_skeleton_accepts_well_formed_unavailable_resources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_complete_skeleton(root)
            report = validate_resources(root, "skeleton", None)
            self.assertTrue(report.ok)
            self.assertFalse(report.ready)
            self.assertEqual(report.errors, ())

    def test_runtime_rejects_unavailable_prototype_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_complete_skeleton(root)
            report = validate_resources(root, "runtime", "prototype")
            self.assertTrue(report.ok)
            self.assertFalse(report.ready)
            self.assertIn("resource_not_ready: generate-prototype", report.errors)

    def test_runtime_accepts_discovery_contracts(self) -> None:
        report = validate_resources(SKILL_ROOT, "runtime", "discovery")
        self.assertTrue(report.ok, report.errors)
        self.assertTrue(report.ready, report.errors)

    def test_runtime_accepts_planning_contracts(self) -> None:
        report = validate_resources(SKILL_ROOT, "runtime", "planning")
        self.assertTrue(report.ok, report.errors)
        self.assertTrue(report.ready, report.errors)

    def test_runtime_accepts_integrated_generation_resources(self) -> None:
        report = validate_resources(SKILL_ROOT, "runtime", "integrated")
        self.assertTrue(report.ok, report.errors)
        self.assertTrue(report.ready, report.errors)

    def test_integrated_stage_requires_aesthetic_quality_resources(self) -> None:
        required = (
            "references/design-contract.md",
            "references/design-contract-schema.json",
            "references/visual-audit-schema.json",
            "scripts/validate_design_contract.py",
            "scripts/validate_visual_audit.py",
        )
        for relative in required:
            with self.subTest(
                relative=relative
            ), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / "skill"
                shutil.copytree(SKILL_ROOT, root)
                (root / relative).unlink()
                report = validate_resources(root, "runtime", "integrated")
                self.assertFalse(report.ok)
                self.assertIn(
                    f"missing_aesthetic_quality_file: {relative}",
                    report.errors,
                )

    def test_integrated_stage_rejects_unready_repair_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "skill"
            shutil.copytree(SKILL_ROOT, root)
            write_prompt(root, "repair-local-issues", ready=False)
            report = validate_resources(root, "runtime", "integrated")
            self.assertTrue(report.ok, report.errors)
            self.assertFalse(report.ready)
            self.assertIn("resource_not_ready: repair-local-issues", report.errors)

    def test_skeleton_rejects_missing_site_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_complete_skeleton(root)
            (root / "references" / "site-planning-contract.md").unlink()
            report = validate_resources(root, "skeleton", None)
            self.assertFalse(report.ok)
            self.assertIn(
                "missing_contract: site-planning-contract",
                report.errors,
            )

    def test_discovery_rejects_missing_visual_companion_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_complete_skeleton(root)
            missing = "scripts/visual_companion/launch.cjs"
            (root / missing).unlink()
            report = validate_resources(root, "runtime", "discovery")
            self.assertFalse(report.ok)
            self.assertIn(
                f"missing_visual_companion: {missing}",
                report.errors,
            )

    def test_runtime_accepts_catalog_only_media_direction_when_reference_library_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_complete_skeleton(root)
            write_prompt(root, "analyze-reference", ready=True)
            write_prompt(root, "direct-media-art", ready=True)
            report = validate_resources(root, "runtime", "media-direction")
            self.assertTrue(report.ok)
            self.assertTrue(report.ready)
            self.assertEqual(report.errors, ())

    def test_runtime_accepts_ready_prompt_and_reference_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_complete_skeleton(root)
            write_prompt(root, "analyze-reference", ready=True)
            write_prompt(root, "direct-media-art", ready=True)
            write_manifest(root, ready=True)
            report = validate_resources(root, "runtime", "media-direction")
            self.assertTrue(report.ok)
            self.assertTrue(report.ready)
            self.assertEqual(report.errors, ())

    def test_runtime_rejects_missing_reference_image(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_complete_skeleton(root)
            write_prompt(root, "analyze-reference", ready=True)
            write_prompt(root, "direct-media-art", ready=True)
            write_manifest(root, ready=True)
            (root / "assets" / "reference-library" / "editorial-01.png").unlink()
            report = validate_resources(root, "runtime", "media-direction")
            self.assertFalse(report.ok)
            self.assertFalse(report.ready)
            self.assertIn("missing_reference_asset: editorial-01.png", report.errors)


    def test_runtime_media_direction_reads_workspace_reference_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_complete_skeleton(root)
            write_prompt(root, "analyze-reference", ready=True)
            write_prompt(root, "direct-media-art", ready=True)
            write_workspace_manifest(root)
            report = validate_resources(root, "runtime", "media-direction", workspace_root=root)
            self.assertTrue(report.ok)
            self.assertTrue(report.ready)
            self.assertEqual(report.errors, ())

    def test_old_style_stage_is_invalid(self) -> None:
        report = validate_resources(SKILL_ROOT, "runtime", "style")
        self.assertFalse(report.ok)
        self.assertIn("invalid_stage: style", report.errors)

    def test_runtime_accepts_motion_enhancement_without_a_recipe_catalog(self) -> None:
        report = validate_resources(SKILL_ROOT, "runtime", "motion-enhancement")
        self.assertTrue(report.ok, report.errors)
        self.assertTrue(report.ready, report.errors)

    def test_runtime_video_upgrade_requires_only_the_ready_upgrade_prompt(self) -> None:
        report = validate_resources(SKILL_ROOT, "runtime", "video-upgrade")
        self.assertTrue(report.ok, report.errors)
        self.assertTrue(report.ready, report.errors)

    def test_malformed_prompt_header_is_invalid_in_all_modes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_complete_skeleton(root)
            prompt_path = root / "prompts" / "01-generate-prototype.md"
            prompt_path.write_text("not frontmatter", encoding="utf-8")
            report = validate_resources(root, "skeleton", None)
            self.assertFalse(report.ok)
            self.assertFalse(report.ready)
            self.assertTrue(any("invalid_prompt" in error for error in report.errors))


if __name__ == "__main__":
    unittest.main()
