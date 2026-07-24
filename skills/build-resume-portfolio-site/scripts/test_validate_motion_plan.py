from __future__ import annotations

import unittest

from validate_motion_plan import validate_media_slot, validate_selection


ALL_RECIPE_IDS = frozenset({"recipe-a", "recipe-b", "recipe-c", "effect-a", "effect-b", "effect-c"})
PRESERVE = [
    "resume_facts",
    "section_order",
    "palette",
    "typography",
    "responsive_hierarchy",
    "confirmed_media_direction_baseline",
]


def valid_selection(
    *,
    primary: list[str] | None = None,
    secondary: list[str] | None = None,
    items: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    primary = primary if primary is not None else ["recipe-a"]
    secondary = secondary if secondary is not None else []
    recipe_ids = primary + secondary
    if items is None:
        items = [
            {
                "id": recipe_id,
                "source": "MotionSite",
                "target": f"#{recipe_id}",
                "purpose": "reinforce the confirmed hierarchy",
                "controllers": ["scroll"],
                "dependencies": [],
                "conflict_resolution": "",
                "cleanup": "dispose observers on unmount",
                "mobile": "simplified",
                "reduced_motion": "static",
                "fallback": "static CSS treatment",
            }
            for recipe_id in recipe_ids
        ]
    return {
        "primary_recipe_ids": primary,
        "secondary_effect_ids": secondary,
        "items": items,
        "preserve": PRESERVE,
    }


class MotionPlanTests(unittest.TestCase):
    def test_selection_accepts_multiple_compatible_recipes(self) -> None:
        data = valid_selection(
            primary=["recipe-a", "recipe-b", "recipe-c"],
            secondary=["effect-a", "effect-b", "effect-c"],
        )
        report = validate_selection(data, ALL_RECIPE_IDS)
        self.assertTrue(report.ok, report.errors)

    def test_selection_rejects_unresolved_target_controller_conflict(self) -> None:
        data = valid_selection(
            primary=["recipe-a", "recipe-b"],
            items=[
                motion_item("recipe-a", "#projects", ["scroll"]),
                motion_item("recipe-b", "#projects", ["scroll"]),
            ],
        )
        report = validate_selection(data, ALL_RECIPE_IDS)
        self.assertIn("unresolved_selection_conflict: #projects:scroll", report.errors)

    def test_selection_rejects_duplicate_recipe_ids(self) -> None:
        data = valid_selection(primary=["recipe-a", "recipe-a"])
        report = validate_selection(data, ALL_RECIPE_IDS)
        self.assertIn("duplicate_recipe_id: recipe-a", report.errors)

    def test_selection_accepts_a_documented_conflict_resolution(self) -> None:
        data = valid_selection(
            primary=["recipe-a", "recipe-b"],
            items=[
                motion_item("recipe-a", "#projects", ["scroll"]),
                motion_item(
                    "recipe-b",
                    "#projects",
                    ["scroll"],
                    conflict_resolution="share the scroll timeline with recipe-a",
                ),
            ],
        )
        report = validate_selection(data, ALL_RECIPE_IDS)
        self.assertTrue(report.ok, report.errors)

    def test_selection_requires_a_complete_item_contract(self) -> None:
        data = valid_selection(items=[{"id": "recipe-a"}])
        report = validate_selection(data, ALL_RECIPE_IDS)
        self.assertIn("invalid_motion_item: recipe-a", report.errors)

    def test_slot_requires_reference_and_resolved_placement(self) -> None:
        report = validate_media_slot(
            {"recipe_id": "a", "placement_reference": {}, "playback": {}, "preserve": []},
            {"id": "a"},
        )
        self.assertIn("missing_resolved_placement", report.errors)

    def test_slot_rejects_scroll_or_pointer_linked_playback(self) -> None:
        report = validate_media_slot(
            {
                "recipe_id": "a",
                "placement_reference": {},
                "resolved_placement": {"layer": "background", "fit": "cover"},
                "playback": {"mode": "passive_loop", "scroll_linked": True, "pointer_linked": False},
                "preserve": [],
            },
            {"id": "a"},
        )
        self.assertIn("interactive_video_forbidden", report.errors)

    def test_slot_requires_preserved_theme_content_and_section_order(self) -> None:
        report = validate_media_slot(
            {
                "recipe_id": "a",
                "placement_reference": {},
                "resolved_placement": {"layer": "content_media", "fit": "contain"},
                "playback": {"mode": "passive_loop", "scroll_linked": False, "pointer_linked": False},
                "preserve": ["resume_facts"],
            },
            {"id": "a"},
        )
        self.assertIn("missing_preserve_rules", report.errors)


def motion_item(
    recipe_id: str,
    target: str,
    controllers: list[str],
    *,
    conflict_resolution: str = "",
) -> dict[str, object]:
    return {
        "id": recipe_id,
        "source": "MotionSite",
        "target": target,
        "purpose": "reinforce the confirmed hierarchy",
        "controllers": controllers,
        "dependencies": [],
        "conflict_resolution": conflict_resolution,
        "cleanup": "dispose observers on unmount",
        "mobile": "simplified",
        "reduced_motion": "static",
        "fallback": "static CSS treatment",
    }


if __name__ == "__main__":
    unittest.main()
