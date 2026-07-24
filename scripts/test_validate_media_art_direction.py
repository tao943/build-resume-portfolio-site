from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_media_art_direction import validate_media_art_direction


def valid_report(effect_count: int = 0) -> dict[str, object]:
    return {
        "schema_version": 1,
        "design_read": {
            "page_kind": "portfolio",
            "audience": "hiring managers",
            "vibe": "evidence-led editorial",
        },
        "visual_thesis": "Editorial proof with a restrained interactive gallery.",
        "energy_curve": [{"section_id": "hero", "intensity": "quiet", "reason": "Orient readers."}],
        "image_analysis": [
            {
                "image_id": "portrait",
                "image_role": "portrait",
                "factual_meaning": "A professional portrait of the candidate.",
                "immutable_facts": ["candidate identity", "professional setting"],
            }
        ],
        "internal_directions": [
            {
                "id": "editorial",
                "name": "Editorial proof",
                "summary": "A readable editorial gallery.",
                "comparison": {
                    "beauty": "high", "content": "high", "narrative": "high",
                    "coherence": "high", "device": "safe", "risk": "low",
                },
            },
            {
                "id": "gallery",
                "name": "Gallery proof",
                "summary": "A tactile card gallery.",
                "comparison": {
                    "beauty": "high", "content": "high", "narrative": "medium",
                    "coherence": "high", "device": "safe", "risk": "medium",
                },
            },
        ],
        "selected_direction_id": "editorial",
        "selection_reason": "It supports evidence and remains usable on touch devices.",
        "section_directions": [
            {
                "section_id": "hero",
                "image_ids": ["portrait"],
                "composition": "layered editorial portrait",
                "effects": [f"effect-{index}" for index in range(effect_count)],
                "purpose": "Introduce the candidate without obscuring facts.",
                "controllers": [],
                "mobile": "Show the portrait in a static single-column layout.",
                "reduced_motion": "Keep the portrait and disable transforms.",
            }
        ],
        "interaction_compatibility": [],
        "media_upgrades": [],
        "responsive_strategy": {
            "desktop": "Keep the editorial gallery beside the evidence copy.",
            "tablet": "Stack the gallery after the evidence copy.",
            "mobile": "Use one readable media column.",
            "coarse_pointer": "Replace hover controls with visible tap controls.",
        },
        "reduced_motion_strategy": {
            "trigger": "prefers-reduced-motion",
            "replacement": "Use static media and no transforms.",
            "content_visibility": "Keep captions and factual media visible.",
        },
        "implementation_choices": ["CSS grid"],
        "preserve": ["resume facts"],
    }


def valid_inventory() -> dict[str, object]:
    return {
        "schema_version": 1,
        "assets": [
            {
                "id": "portrait",
                "factual_meaning": "A professional portrait of the candidate.",
                "immutable_facts": ["candidate identity", "professional setting"],
                "role": "portrait",
                "source": "user-provided",
            }
        ]
    }


class ValidateMediaArtDirectionTests(unittest.TestCase):
    def write(self, payload: dict[str, object], filename: str = "media-art-direction.json") -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / filename
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def validate(self, payload: dict[str, object], inventory: dict[str, object] | None = None):
        report_path = self.write(payload)
        inventory_path = self.write(inventory or valid_inventory(), "media-inventory.json")
        return validate_media_art_direction(report_path, inventory_path)

    def test_valid_report_allows_eight_effects(self) -> None:
        report = self.validate(valid_report(effect_count=8))
        self.assertTrue(report.ok, report.errors)

    def test_selected_direction_must_exist(self) -> None:
        payload = valid_report()
        payload["selected_direction_id"] = "missing"
        report = self.validate(payload)
        self.assertIn("selected_direction_missing", report.errors)

    def test_controller_conflict_requires_resolution(self) -> None:
        payload = valid_report()
        payload["interaction_compatibility"] = [
            {"controller": "scroll", "owners": ["pan", "video"], "resolution": ""}
        ]
        report = self.validate(payload)
        self.assertIn("interaction_conflict_unresolved: scroll", report.errors)

    def test_section_media_must_be_analyzed_authorized_media(self) -> None:
        payload = valid_report()
        section = payload["section_directions"][0]
        assert isinstance(section, dict)
        section["image_ids"] = ["unapproved"]
        report = self.validate(payload)
        self.assertIn("unauthorized_media_id: unapproved", report.errors)

    def test_present_media_requires_image_analysis(self) -> None:
        payload = valid_report()
        payload["image_analysis"] = []
        report = self.validate(payload)
        self.assertIn("missing_image_analysis", report.errors)

    def test_authorized_media_requires_factual_meaning_and_immutable_facts(self) -> None:
        payload = valid_report()
        image = payload["image_analysis"][0]
        assert isinstance(image, dict)
        image["factual_meaning"] = ""
        image["immutable_facts"] = []
        report = self.validate(payload)
        self.assertIn("missing_factual_meaning: portrait", report.errors)
        self.assertIn("missing_immutable_facts: portrait", report.errors)

    def test_section_requires_mobile_and_reduced_motion_fallbacks(self) -> None:
        payload = valid_report()
        section = payload["section_directions"][0]
        assert isinstance(section, dict)
        section["mobile"] = ""
        section["reduced_motion"] = ""
        report = self.validate(payload)
        self.assertIn("missing_section_mobile: hero", report.errors)
        self.assertIn("missing_section_reduced_motion: hero", report.errors)

    def test_report_requires_an_explicit_inventory_even_without_media(self) -> None:
        payload = valid_report()
        payload["image_analysis"] = []
        section = payload["section_directions"][0]
        assert isinstance(section, dict)
        section["image_ids"] = []
        report = validate_media_art_direction(self.write(payload), None)
        self.assertIn("authorized_media_inventory_required", report.errors)

    def test_empty_versioned_inventory_allows_a_report_without_media(self) -> None:
        payload = valid_report()
        payload["image_analysis"] = []
        section = payload["section_directions"][0]
        assert isinstance(section, dict)
        section["image_ids"] = []
        report = self.validate(payload, {"schema_version": 1, "assets": []})
        self.assertTrue(report.ok, report.errors)

    def test_rejects_forged_media_id_not_in_trusted_inventory(self) -> None:
        payload = valid_report()
        image = payload["image_analysis"][0]
        assert isinstance(image, dict)
        image["image_id"] = "forged"
        section = payload["section_directions"][0]
        assert isinstance(section, dict)
        section["image_ids"] = ["forged"]
        report = self.validate(payload)
        self.assertIn("unauthorized_media_id: forged", report.errors)

    def test_rejects_factual_changes_to_trusted_media(self) -> None:
        payload = valid_report()
        image = payload["image_analysis"][0]
        assert isinstance(image, dict)
        image["factual_meaning"] = "An invented executive portrait."
        image["immutable_facts"] = ["invented identity"]
        report = self.validate(payload)
        self.assertIn("factual_meaning_mismatch: portrait", report.errors)
        self.assertIn("immutable_facts_mismatch: portrait", report.errors)

    def test_rejects_schema_extra_fields_and_invalid_energy_enum(self) -> None:
        payload = valid_report()
        payload["surprise"] = "not in the schema"
        beat = payload["energy_curve"][0]
        assert isinstance(beat, dict)
        beat["intensity"] = "loud"
        report = self.validate(payload)
        self.assertIn("unexpected_report_field: surprise", report.errors)
        self.assertIn("invalid_energy_intensity: hero", report.errors)

    def test_duplicate_controller_ownership_requires_each_owner_resolution(self) -> None:
        payload = valid_report()
        section = payload["section_directions"][0]
        assert isinstance(section, dict)
        section["controllers"] = [
            {
                "id": "scroll-owner",
                "type": "scroll",
                "targets": ["hero-media"],
                "properties": ["transform"],
                "handoff": "Scroll owns the base transform.",
                "conflict_resolution": "Pointer uses an isolated layer.",
            },
            {
                "id": "pointer-owner",
                "type": "pointer",
                "targets": ["hero-media"],
                "properties": ["transform"],
                "handoff": "",
                "conflict_resolution": "Pointer hands off before scroll resumes.",
            },
        ]
        report = self.validate(payload)
        self.assertIn("missing_controller_handoff: pointer-owner", report.errors)
        self.assertIn("controller_conflict_unresolved: hero-media.transform", report.errors)


if __name__ == "__main__":
    unittest.main()
