from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_workflow_route.py"


def valid_route() -> dict:
    return {
        "schema_version": 1,
        "route": "site-fast-change",
        "reason": "bounded copy correction on a confirmed site",
        "content_package_status": "ready",
        "confirmed_artifact": "versions/v4-motion",
        "strategic_scope_changed": False,
        "structural_scope_changed": False,
        "affected_files": ["src/content/hero.js"],
        "verification": ["npm run build"],
        "rollback_baseline": "versions/v4-motion",
    }


class WorkflowRouteValidatorTests(unittest.TestCase):
    def run_validator(self, payload: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "route.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_bounded_fast_change(self) -> None:
        self.assertEqual(self.run_validator(valid_route()).returncode, 0)

    def test_rejects_fast_change_without_confirmed_artifact(self) -> None:
        payload = valid_route()
        payload["confirmed_artifact"] = None
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_fast_change_for_structural_scope(self) -> None:
        payload = valid_route()
        payload["structural_scope_changed"] = True
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_fast_change_for_strategic_scope(self) -> None:
        payload = valid_route()
        payload["strategic_scope_changed"] = True
        self.assertEqual(self.run_validator(payload).returncode, 1)


if __name__ == "__main__":
    unittest.main()
