from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("migrate_build_state.py")


def version_three_state() -> dict:
    return {
        "schema_version": 3,
        "skill_version": "1.1.0-react-vite",
        "stage": "complete",
        "last_confirmed_artifact": "versions/v4-motion",
        "confirmations": {
            "prototype": True,
            "media_direction": True,
            "motion": True,
        },
        "current_artifact": "versions/v4-motion",
        "current_preview": "preview/dist/index.html",
        "attempted_direction_ids": ["editorial"],
        "attempted_media_direction_ids": [],
        "visual_repair_round": 0,
    }


class MigrateBuildStateTests(unittest.TestCase):
    def load_module(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("migrate_build_state", SCRIPT)
        if spec is None or spec.loader is None:
            raise AssertionError("unable to load migration module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_preserves_state_and_adds_v4_workflow_fields(self) -> None:
        module = self.load_module()
        original = version_three_state()
        migrated = module.migrate(original)

        for key, value in original.items():
            if key not in {"schema_version", "skill_version"}:
                self.assertEqual(migrated[key], value)
        self.assertEqual(original["schema_version"], 3)
        self.assertEqual(migrated["schema_version"], 4)
        self.assertEqual(migrated["skill_version"], "1.2.0-react-vite")
        self.assertEqual(migrated["workflow_mode"], "fast-change-eligible")
        self.assertEqual(
            migrated["discovery"],
            {"site_design_approved": False, "site_plan_validated": False},
        )

    def test_without_confirmed_artifact_requires_full_workflow(self) -> None:
        module = self.load_module()
        state = version_three_state()
        state["last_confirmed_artifact"] = None
        state["confirmations"] = {
            "prototype": False,
            "media_direction": False,
            "motion": False,
        }
        self.assertEqual(module.migrate(state)["workflow_mode"], "full")

    def test_rejects_unsupported_version_and_malformed_confirmation(self) -> None:
        module = self.load_module()
        unsupported = version_three_state()
        unsupported["schema_version"] = 2
        with self.assertRaises(ValueError):
            module.migrate(unsupported)

        malformed = version_three_state()
        malformed["confirmations"]["motion"] = "yes"
        with self.assertRaises(ValueError):
            module.migrate(malformed)

    def test_rejects_confirmation_without_snapshot_reference(self) -> None:
        module = self.load_module()
        state = version_three_state()
        state["last_confirmed_artifact"] = None
        with self.assertRaises(ValueError):
            module.migrate(state)

    def test_cli_is_atomic_and_refuses_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "build-state-v3.json"
            output = root / "build-state-v4.json"
            source.write_text(json.dumps(version_three_state()), encoding="utf-8")

            first = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["schema_version"], 4)
            self.assertEqual(
                json.loads(source.read_text(encoding="utf-8"))["schema_version"],
                3,
            )

            second = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("output already exists", second.stderr)


if __name__ == "__main__":
    unittest.main()
