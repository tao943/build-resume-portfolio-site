from __future__ import annotations

import json
import unittest
from pathlib import Path

from structure_seed_selector import filter_feasible_seeds


ROOT = Path(__file__).resolve().parents[1]


class StructureSeedCapacityTests(unittest.TestCase):
    def test_all_seeds_are_classified_across_capacity_matrix(self) -> None:
        catalog = json.loads((ROOT / "assets" / "structure-seeds" / "catalog.json").read_text(encoding="utf-8"))
        profiles = [
            {"project_count": 1, "experience_count": 0, "skill_count": 3, "copy_density": "low", "media_profile": "none", "max_layout_cost": 3, "max_motion_cost": 3, "allow_three_d": False},
            {"project_count": 4, "experience_count": 3, "skill_count": 6, "copy_density": "medium", "media_profile": "limited", "max_layout_cost": 3, "max_motion_cost": 3, "allow_three_d": False},
            {"project_count": 10, "experience_count": 8, "skill_count": 12, "copy_density": "high", "media_profile": "rich", "max_layout_cost": 3, "max_motion_cost": 3, "allow_three_d": True},
        ]
        seed_ids = {seed["id"] for seed in catalog["seeds"]}
        accepted_somewhere: set[str] = set()
        for profile in profiles:
            result = filter_feasible_seeds(catalog, profile)
            accepted = {seed["id"] for seed in result["accepted"]}
            rejected = {item["id"] for item in result["rejected"]}
            self.assertEqual(accepted | rejected, seed_ids)
            self.assertFalse(accepted & rejected)
            self.assertTrue(all(item["reason_codes"] for item in result["rejected"]))
            accepted_somewhere |= accepted
        self.assertEqual(accepted_somewhere, seed_ids)
        self.assertTrue(all(seed["responsive_transformations"] for seed in catalog["seeds"]))


if __name__ == "__main__":
    unittest.main()
