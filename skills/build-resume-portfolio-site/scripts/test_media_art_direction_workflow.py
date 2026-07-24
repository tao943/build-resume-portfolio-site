"""Contract checks for the media art-direction workflow resources."""

import json
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = SKILL_ROOT / "prompts" / "03-direct-media-art.md"
CONTRACT_PATH = SKILL_ROOT / "references" / "media-art-direction-contract.md"
SCHEMA_PATH = SKILL_ROOT / "references" / "media-art-direction-schema.json"
WORKFLOW_PATH = SKILL_ROOT / "references" / "workflow-contract.md"
ARTIFACT_LAYOUT_PATH = SKILL_ROOT / "references" / "artifact-layout.md"


class MediaArtDirectionWorkflowTests(unittest.TestCase):
    def test_prompt_declares_the_required_workflow_and_vocabulary(self):
        prompt = PROMPT_PATH.read_text(encoding="utf-8")

        for marker in (
            "resource_id: direct-media-art",
            "reports/media-art-direction.json",
            "internal directions",
            "one best candidate",
            "same React + Vite project",
            "3D Coverflow",
            "Dome Gallery",
            "Hover Image Trail",
            "Sticky Stack",
            "video sequence",
            "interaction ownership",
            "no numeric effect cap",
            "user-provided media",
            "factual meaning",
        ):
            self.assertIn(marker, prompt)

    def test_contract_covers_energy_image_roles_and_accessible_spatial_modes(self):
        contract = CONTRACT_PATH.read_text(encoding="utf-8")

        for marker in (
            "visual energy curve",
            "image role",
            "controller",
            "conflict resolution",
            "2.5D",
            "real 3D",
            "coarse pointer",
            "prefers-reduced-motion",
            "deterministic workflow validator",
            "image_analysis",
            "media-inventory.json",
            "controller ID",
        ):
            self.assertIn(marker, contract)

    def test_schema_is_portable_and_requires_structured_controller_ownership(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        properties = schema["properties"]
        required = set(schema["required"])
        required_fields = {
            "schema_version",
            "design_read",
            "visual_thesis",
            "energy_curve",
            "image_analysis",
            "internal_directions",
            "selected_direction_id",
            "selection_reason",
            "section_directions",
            "interaction_compatibility",
            "media_upgrades",
            "responsive_strategy",
            "reduced_motion_strategy",
            "implementation_choices",
            "preserve",
        }

        self.assertTrue(required_fields.issubset(required))
        self.assertNotIn("max_effects", properties)
        self.assertNotIn("maxItems", properties)
        self.assertEqual(properties["design_read"]["$ref"], "#/$defs/design_read")
        self.assertEqual(properties["responsive_strategy"]["$ref"], "#/$defs/responsive_strategy")
        self.assertEqual(properties["reduced_motion_strategy"]["$ref"], "#/$defs/reduced_motion_strategy")
        self.assertTrue(
            {"page_kind", "audience", "vibe"}.issubset(schema["$defs"]["design_read"]["required"])
        )
        self.assertTrue(
            {"desktop", "tablet", "mobile", "coarse_pointer"}.issubset(
                schema["$defs"]["responsive_strategy"]["required"]
            )
        )
        self.assertTrue(
            {"trigger", "replacement", "content_visibility"}.issubset(
                schema["$defs"]["reduced_motion_strategy"]["required"]
            )
        )

        directions = properties["internal_directions"]
        self.assertGreaterEqual(directions["minItems"], 2)
        self.assertEqual(properties["selected_direction_id"]["type"], "string")
        self.assertIn("deterministic workflow validator", schema["$comment"])

        def walk(value):
            if isinstance(value, dict):
                self.assertNotIn("$data", value)
                for nested in value.values():
                    walk(nested)
            elif isinstance(value, list):
                for nested in value:
                    walk(nested)

        walk(schema)

        section_directions = properties["section_directions"]
        self.assertGreaterEqual(section_directions["minItems"], 1)
        self.assertTrue(
            {
                "section_id",
                "image_ids",
                "composition",
                "effects",
                "purpose",
                "controllers",
                "mobile",
                "reduced_motion",
            }.issubset(set(schema["$defs"]["section_direction"]["required"]))
        )

        controller = schema["$defs"]["interaction_controller"]
        self.assertTrue(
            {"id", "type", "targets", "properties", "handoff", "conflict_resolution"}
            .issubset(set(controller["required"]))
        )
        self.assertEqual(
            schema["$defs"]["section_direction"]["properties"]["controllers"]["items"]["$ref"],
            "#/$defs/interaction_controller",
        )
        compatibility = schema["$defs"]["interaction_compatibility"]
        self.assertEqual(
            properties["interaction_compatibility"]["items"]["$ref"],
            "#/$defs/interaction_compatibility",
        )
        self.assertTrue({"controller", "owners", "resolution"}.issubset(compatibility["required"]))

        valid_controller = {
            "id": "hero-scroll",
            "type": "scroll",
            "targets": ["hero-media"],
            "properties": ["transform"],
            "handoff": "pointer controls an isolated foreground layer",
            "conflict_resolution": "scroll owns the hero-media transform",
        }
        self.assertTrue(
            {"id", "type", "targets", "properties", "handoff", "conflict_resolution"}
            .issubset(valid_controller)
        )
        invalid_controller = valid_controller.copy()
        del invalid_controller["conflict_resolution"]
        self.assertFalse(
            {"id", "type", "targets", "properties", "handoff", "conflict_resolution"}
            .issubset(invalid_controller)
        )

    def test_workflow_persists_the_media_direction_gate_and_artifacts(self):
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        layout = ARTIFACT_LAYOUT_PATH.read_text(encoding="utf-8")

        for marker in (
            "prototype_waiting_confirmation --confirm--> media_direction_generating",
            "media_direction_generating -> media_direction_waiting_confirmation",
            "media_direction_waiting_confirmation --confirm--> screenshot_auditing",
            "media_direction_waiting_confirmation --reject--> media_direction_generating",
            "confirmations.media_direction",
            "selected_media_direction_id",
            "attempted_media_direction_ids",
            "versions/v2-media-direction",
            "reports/media-art-direction.json",
            "reports/media-inventory.json",
            '"schema_version": 3',
            "reject unsupported old state schemas",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, workflow + layout)

        self.assertNotIn("style_waiting_confirmation", workflow + layout)
        self.assertNotIn("v2-styled", workflow + layout)

    def test_optional_motion_enhancement_is_not_a_fourth_gate(self):
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

        self.assertIn("## Confirmation gates", workflow)
        self.assertIn("optional branch", workflow)
        self.assertNotIn("a deliberate gate", workflow)

    def test_prompt_and_skill_require_an_explicit_empty_or_populated_inventory(self):
        prompt = PROMPT_PATH.read_text(encoding="utf-8")
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        for marker in (
            '"schema_version": 1, "assets": []',
            "design_read",
            "responsive_strategy",
            "reduced_motion_strategy",
            "--media-inventory",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, prompt + skill)


if __name__ == "__main__":
    unittest.main()
