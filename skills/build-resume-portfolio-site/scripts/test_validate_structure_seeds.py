from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
VALIDATOR_PATH = SCRIPT_DIR / "validate_structure_seeds.py"
CATALOG_PATH = SKILL_ROOT / "assets" / "structure-seeds" / "catalog.json"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_structure_seeds", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"missing validator: {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class StructureSeedCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()
        self.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    def test_version_one_catalog_has_twelve_expected_seeds(self) -> None:
        self.assertEqual(self.module.validate_catalog(self.catalog), [])
        self.assertEqual(
            {seed["id"] for seed in self.catalog["seeds"]},
            {
                "split-narrative", "poster-to-evidence", "pinned-chapter-stage",
                "horizontal-project-reel", "index-and-canvas", "editorial-zigzag",
                "layered-evidence-deck", "orbit-and-anchors",
                "continuous-timeline-ribbon", "architectural-breakout-grid",
                "cinematic-act-sequence", "constellation-map",
            },
        )

    def test_rejects_duplicate_id_and_missing_mobile_contract(self) -> None:
        duplicate = copy.deepcopy(self.catalog)
        duplicate["seeds"][1]["id"] = duplicate["seeds"][0]["id"]
        self.assertTrue(any("duplicate seed id" in e for e in self.module.validate_catalog(duplicate)))
        missing = copy.deepcopy(self.catalog)
        missing["seeds"][0]["responsive_transformations"] = []
        self.assertTrue(any("responsive_transformations" in e for e in self.module.validate_catalog(missing)))

    def test_rejects_template_payload_and_out_of_range_cost(self) -> None:
        invalid = copy.deepcopy(self.catalog)
        invalid["seeds"][0]["jsx"] = "<Hero />"
        invalid["seeds"][0]["cost"]["motion"] = 4
        errors = self.module.validate_catalog(invalid)
        self.assertTrue(any("forbidden" in e for e in errors), errors)
        self.assertTrue(any("cost.motion" in e for e in errors), errors)

    def test_every_seed_has_canonical_signature_and_static_motion_slot(self) -> None:
        for seed in self.catalog["seeds"]:
            self.assertEqual(set(seed["canonical_signature"]), set(self.module.SIGNATURE_FIELDS))
            self.assertTrue(seed["motion_slots"])
            self.assertTrue(all(slot["optional"] for slot in seed["motion_slots"]))
            self.assertTrue(seed["invariants"])
            self.assertTrue(seed["anti_degeneracy_rules"])


if __name__ == "__main__":
    unittest.main()
