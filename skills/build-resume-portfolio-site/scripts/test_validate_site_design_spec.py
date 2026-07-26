from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_site_design_spec.py"


def valid_spec() -> dict:
    return {
        "schema_version": 1,
        "spec_id": "site-spec-1",
        "workflow_mode": "full",
        "content_revision": 1,
        "visual_protagonist": "project outcomes",
        "fixed_constraints": ["preserve approved copy"],
        "open_ceiling": ["composition", "motion language"],
        "avoid": ["generic card grid"],
        "alternatives": [
            {
                "id": "editorial",
                "family": "radical editorial",
                "tradeoffs": ["denser reading rhythm"],
            },
            {
                "id": "cinematic",
                "family": "cinematic portfolio",
                "tradeoffs": ["higher media dependency"],
            },
        ],
        "selected_alternative_id": "editorial",
        "composition_commitment": "asymmetric editorial stage",
        "type_color_character": "high-contrast serif and restrained yellow",
        "representative_interaction": (
            "project selection updates one detail panel"
        ),
        "approval": {"status": "user_approved", "source": "explicit_user"},
    }


class SiteDesignSpecValidatorTests(unittest.TestCase):
    def run_validator(self, payload: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spec.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_valid_full_spec(self) -> None:
        self.assertEqual(self.run_validator(valid_spec()).returncode, 0)

    def test_rejects_one_full_mode_alternative(self) -> None:
        payload = valid_spec()
        payload["alternatives"] = payload["alternatives"][:1]
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_duplicate_layout_families(self) -> None:
        payload = valid_spec()
        payload["alternatives"][1]["family"] = "radical editorial"
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_fixed_and_avoid_overlap(self) -> None:
        payload = valid_spec()
        payload["avoid"] = ["preserve approved copy"]
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_missing_explicit_approval(self) -> None:
        payload = valid_spec()
        payload["approval"]["source"] = "inferred"
        self.assertEqual(self.run_validator(payload).returncode, 1)


if __name__ == "__main__":
    unittest.main()
