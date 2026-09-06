from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_validate_site_design_spec import valid_spec


PATH = Path(__file__).resolve().parent / "migrate_site_design_spec_v4.py"


def load_module():
    spec = importlib.util.spec_from_file_location("migrate_site_design_spec_v4", PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"missing migrator: {PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SiteDesignSpecMigrationTests(unittest.TestCase):
    def test_migration_preserves_non_structure_decisions_and_approval(self) -> None:
        module = load_module()
        source = valid_spec()
        migrated = module.migrate(source, reason="user requested structural exploration")
        self.assertEqual(migrated["schema_version"], 4)
        self.assertEqual(migrated["decisions"]["structure"]["status"], "agent_delegated")
        for key in ("typography", "color", "media", "primary_motion", "secondary_motion"):
            self.assertEqual(migrated["decisions"][key], source["decisions"][key])
        self.assertEqual(migrated["requirements_approval"], source["requirements_approval"])
        self.assertEqual(migrated["migration"]["source_schema_version"], 3)
        self.assertEqual(migrated["migration"]["invalidated_artifacts"], ["design-intelligence", "creative-direction", "design-contract", "motion-plan", "visual-audit"])

    def test_refuses_silent_or_repeat_migration(self) -> None:
        module = load_module()
        with self.assertRaisesRegex(ValueError, "reason"):
            module.migrate(valid_spec(), reason="")
        source = valid_spec()
        source["schema_version"] = 4
        with self.assertRaisesRegex(ValueError, "schema version 3"):
            module.migrate(source, reason="explicit")


if __name__ == "__main__":
    unittest.main()
