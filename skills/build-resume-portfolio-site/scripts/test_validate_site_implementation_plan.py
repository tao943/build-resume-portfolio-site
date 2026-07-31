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
        "schema_version": 2,
        "design_spec_id": "site-spec-1",
        "todo_plan": ".resume-site-work/reports/site-todo-plan.md",
        "todo_plan_approval": {
            "status": "user_approved",
            "source": "explicit_user",
            "channel": "conversation",
        },
        "generation_mode": "one-integrated-site",
        "strategy": "single-agent",
        "multi_agent_authorized": False,
        "multi_agent_plan": None,
        "tasks": [
            {
                "id": "integrated-site",
                "depends_on": [],
                "files": ["src/App.jsx", "src/styles.css"],
                "consumes": [
                    "approved-copy.json",
                    "site-design-spec.json",
                ],
                "produces": ["complete integrated portfolio"],
                "acceptance": [
                    "Representative interaction is rendered."
                ],
                "verification": [
                    "python validate_vite_project.py "
                    ".resume-site-work/site --stage integrated",
                    "npm run build",
                ],
            }
        ],
        "rollback_baseline": "empty/new site",
        "snapshot_target": "versions/v1-integrated",
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

    def test_rejects_missing_readable_todo_plan_path(self) -> None:
        payload = valid_plan()
        payload.pop("todo_plan")
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_todo_plan_outside_reports(self) -> None:
        payload = valid_plan()
        payload["todo_plan"] = "docs/site-todo-plan.md"
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("todo_plan must reference", result.stdout)

    def test_rejects_unapproved_todo_plan(self) -> None:
        payload = valid_plan()
        payload["todo_plan_approval"]["status"] = "pending"
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("todo plan requires user approval", result.stdout)

    def test_rejects_browser_todo_plan_approval(self) -> None:
        payload = valid_plan()
        payload["todo_plan_approval"]["channel"] = "browser"
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "todo plan approval must be explicit and conversational",
            result.stdout,
        )

    def test_rejects_non_integrated_generation_mode(self) -> None:
        payload = valid_plan()
        payload["generation_mode"] = "prototype-first"
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("generation_mode must be one-integrated-site", result.stdout)

    def test_rejects_version_one(self) -> None:
        payload = valid_plan()
        payload["schema_version"] = 1
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("schema_version must be 2", result.stdout)


if __name__ == "__main__":
    unittest.main()
