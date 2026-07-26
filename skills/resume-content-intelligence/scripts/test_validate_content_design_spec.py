from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_content_design_spec.py"


def valid_spec() -> dict:
    return {
        "schema_version": 1,
        "spec_id": "content-spec-1",
        "workflow_mode": "full",
        "inventory_complete": True,
        "target_audience": "frontend hiring team",
        "fixed_facts": ["fact-1"],
        "open_questions": [],
        "alternatives": [
            {
                "id": "evidence-first",
                "thesis": "Lead with verified outcomes",
                "tradeoffs": ["less personal narrative"],
            },
            {
                "id": "project-first",
                "thesis": "Lead with technical projects",
                "tradeoffs": ["work history appears later"],
            },
        ],
        "selected_alternative_id": "evidence-first",
        "decision_rationale": "Matches the target role and strongest evidence.",
        "approval": {"status": "user_approved", "source": "explicit_user"},
    }


class ContentDesignSpecValidatorTests(unittest.TestCase):
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

    def test_rejects_one_alternative_in_full_mode(self) -> None:
        payload = valid_spec()
        payload["alternatives"] = payload["alternatives"][:1]
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_unknown_selected_alternative(self) -> None:
        payload = valid_spec()
        payload["selected_alternative_id"] = "missing"
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_unapproved_strategy(self) -> None:
        payload = valid_spec()
        payload["approval"]["status"] = "draft"
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_placeholder_text(self) -> None:
        payload = valid_spec()
        payload["decision_rationale"] = "TODO"
        self.assertEqual(self.run_validator(payload).returncode, 1)


if __name__ == "__main__":
    unittest.main()
