from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_content_implementation_plan.py"


def valid_plan() -> dict:
    return {
        "schema_version": 1,
        "design_spec_id": "content-spec-1",
        "tasks": [
            {
                "id": "rewrite-project-1",
                "fact_ids": ["fact-1"],
                "evidence_ids": ["evidence-1"],
                "target_files": [
                    ".resume-site-work/input/approved-copy.json"
                ],
                "produces": ["approved_copy.project-1"],
                "blocked_claims": [],
                "verification": [
                    "python validate_content_package.py package.json"
                ],
            }
        ],
        "handoff_criteria": [
            "All visible claims cite facts or explicit confirmation."
        ],
    }


class ContentImplementationPlanValidatorTests(unittest.TestCase):
    def run_validator(self, payload: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_valid_plan(self) -> None:
        self.assertEqual(self.run_validator(valid_plan()).returncode, 0)

    def test_rejects_empty_tasks(self) -> None:
        payload = valid_plan()
        payload["tasks"] = []
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_missing_target_files(self) -> None:
        payload = valid_plan()
        payload["tasks"][0]["target_files"] = []
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_claim_without_facts_evidence_or_block(self) -> None:
        payload = valid_plan()
        task = payload["tasks"][0]
        task["fact_ids"] = []
        task["evidence_ids"] = []
        task["blocked_claims"] = []
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_placeholder_text(self) -> None:
        payload = valid_plan()
        payload["tasks"][0]["produces"] = ["TBD"]
        self.assertEqual(self.run_validator(payload).returncode, 1)


if __name__ == "__main__":
    unittest.main()
