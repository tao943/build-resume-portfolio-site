from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
SELECTOR_PATH = SCRIPT_DIR / "structure_seed_selector.py"
CATALOG_PATH = SKILL_ROOT / "assets" / "structure-seeds" / "catalog.json"


def load_module():
    spec = importlib.util.spec_from_file_location("structure_seed_selector", SELECTOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"missing selector: {SELECTOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class StructureSeedSelectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()
        self.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        self.content = {
            "profile": {"name": "Secret", "role": "Designer", "industry": "Finance"},
            "projects": [{"title": "A"}, {"title": "B"}, {"title": "C"}],
            "experience": [{"title": "X"}],
            "skills": ["one", "two", "three"],
            "contact": {"email": "secret@example.com"},
            "media": {"project_images": 2, "portrait": False},
        }

    def test_profile_is_structural_and_private(self) -> None:
        profile = self.module.build_structural_profile(self.content, {}, {})
        serialized = json.dumps(profile)
        for secret in ("Secret", "Designer", "Finance", "secret@example.com"):
            self.assertNotIn(secret, serialized)
        self.assertEqual(profile["project_count"], 3)

    def test_pair_is_reproducible_distinct_and_history_aware(self) -> None:
        profile = self.module.build_structural_profile(self.content, {}, {})
        first = self.module.select_seed_pair(self.catalog, profile, [], "generation-a")
        second = self.module.select_seed_pair(self.catalog, profile, [], "generation-a")
        self.assertEqual(first, second)
        self.assertNotEqual(first["fit"]["id"], first["novelty"]["id"])
        history = [{"generation_id": "old", "structure_seed": first["fit"]["id"],
                    "structure_origin": "seed", "reading_axis": "vertical",
                    "hero_gravity": "center", "visual_protagonist": "type",
                    "project_pattern": "reveal", "color_strategy": "mono",
                    "motion_family": "none", "surface_language": "flat"}]
        with_history = self.module.select_seed_pair(self.catalog, profile, history, "generation-a")
        self.assertNotEqual(with_history["novelty"]["id"], first["fit"]["id"])

    def test_wildcard_similarity_uses_canonical_values_not_labels_or_order(self) -> None:
        signature = self.catalog["seeds"][0]["canonical_signature"]
        reordered = {key: signature[key] for key in reversed(list(signature))}
        self.assertEqual(self.module.topology_distance(signature, reordered), 0.0)
        changed = dict(signature, axis="radial", anchor="cursor-controlled")
        self.assertGreaterEqual(self.module.topology_distance(signature, changed), 0.35)

    def test_history_write_is_idempotent_and_requires_passed_audit(self) -> None:
        fingerprint = {
            "schema_version": 1, "generation_id": "g1", "structure_origin": "seed",
            "structure_seed": "split-narrative", "reading_axis": "vertical",
            "hero_gravity": "center", "visual_protagonist": "type",
            "project_pattern": "reveal", "color_strategy": "mono",
            "motion_family": "none", "surface_language": "flat",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "visual-fingerprints.json"
            self.module.record_successful_fingerprint(path, fingerprint, audit_passed=False)
            self.assertFalse(path.exists())
            self.module.record_successful_fingerprint(path, fingerprint, audit_passed=True)
            self.module.record_successful_fingerprint(path, dict(fingerprint, color_strategy="drenched"), audit_passed=True)
            history = self.module.load_history(path)
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["color_strategy"], "drenched")

    def test_malformed_history_is_quarantined_not_overwritten(self) -> None:
        fingerprint = {
            "schema_version": 1, "generation_id": "g2", "structure_origin": "wildcard",
            "structure_seed": None, "reading_axis": "radial", "hero_gravity": "center",
            "visual_protagonist": "field", "project_pattern": "cross-link",
            "color_strategy": "mono", "motion_family": "none", "surface_language": "flat",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "visual-fingerprints.json"
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "malformed"):
                self.module.record_successful_fingerprint(path, fingerprint, audit_passed=True)
            self.assertFalse(path.exists())
            quarantined = list(Path(directory).glob("visual-fingerprints.json.corrupt-*"))
            self.assertEqual(len(quarantined), 1)
            self.assertEqual(quarantined[0].read_text(encoding="utf-8"), "{broken")


if __name__ == "__main__":
    unittest.main()
