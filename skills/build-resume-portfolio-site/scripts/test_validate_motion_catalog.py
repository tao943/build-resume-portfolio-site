from __future__ import annotations

import unittest
import json
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

from validate_motion_catalog import EXPECTED_RECIPE_IDS, validate_catalog


CATALOG = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "motion-enhancement"
    / "catalog"
)


class MotionCatalogTests(unittest.TestCase):
    def test_real_catalog_contains_all_eleven_ready_recipes(self) -> None:
        report = validate_catalog(CATALOG)
        self.assertTrue(report.ok, report.errors)
        self.assertTrue(report.ready)
        self.assertEqual(report.recipe_ids, EXPECTED_RECIPE_IDS)

    def test_real_catalog_disables_interactive_video_control(self) -> None:
        report = validate_catalog(CATALOG)
        self.assertFalse(
            any("interactive_video_forbidden" in error for error in report.errors),
            report.errors,
        )

    def test_catalog_accepts_a_source_agnostic_confirmed_baseline(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            catalog = Path(temporary_directory) / "catalog"
            copytree(CATALOG, catalog)
            for recipe_path in (catalog / "recipes").glob("*.json"):
                recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
                recipe["preserve"] = [
                    "resume_facts",
                    "section_order",
                    "palette",
                    "typography",
                    "responsive_hierarchy",
                    "confirmed_media_direction_baseline",
                ]
                recipe_path.write_text(json.dumps(recipe), encoding="utf-8")
            report = validate_catalog(catalog)
        self.assertTrue(report.ok, report.errors)


if __name__ == "__main__":
    unittest.main()
