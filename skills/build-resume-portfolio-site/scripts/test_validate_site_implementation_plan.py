from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_site_implementation_plan.py"


def valid_plan() -> dict:
    return {
        "schema_version": 1,
        "design_spec_id": "site-spec-1",
        "strategy": "single-agent",
        "multi_agent_authorized": False,
        "multi_agent_plan": None,
        "tasks": [
            {
                "id": "prototype-shell",
                "depends_on": [],
                "files": ["src/App.jsx", "src/styles.css"],
                "consumes": [
                    "approved-copy.json",
                    "site-design-spec.json",
                ],
                "produces": ["five-region prototype"],
                "acceptance": [
                    "Representative interaction is rendered."
                ],
                "verification": [
                    "python validate_vite_project.py "
                    ".resume-site-work/site --stage prototype",
                    "npm run build",
                ],
            }
        ],
        "rollback_baseline": "empty/new site",
        "snapshot_target": "versions/v1-prototype",
    }


class SiteImplementationPlanValidatorTests(unittest.TestCase):
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

    def test_accepts_valid_single_agent_plan(self) -> None:
        self.assertEqual(self.run_validator(valid_plan()).returncode, 0)

    def test_rejects_missing_exact_files(self) -> None:
        payload = valid_plan()
        payload["tasks"][0]["files"] = []
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_unknown_dependency(self) -> None:
        payload = valid_plan()
        payload["tasks"][0]["depends_on"] = ["missing"]
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_unauthorized_multi_agent_plan(self) -> None:
        payload = valid_plan()
        payload["strategy"] = "parallel-wave"
        payload["multi_agent_plan"] = (
            ".resume-site-work/reports/multi-agent-implementation.json"
        )
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_parallel_file_overlap(self) -> None:
        payload = valid_plan()
        payload["strategy"] = "parallel-wave"
        payload["multi_agent_authorized"] = True
        payload["multi_agent_plan"] = (
            ".resume-site-work/reports/multi-agent-implementation.json"
        )
        duplicate = dict(payload["tasks"][0])
        duplicate["id"] = "duplicate-owner"
        payload["tasks"].append(duplicate)
        self.assertEqual(self.run_validator(payload).returncode, 1)


if __name__ == "__main__":
    unittest.main()
