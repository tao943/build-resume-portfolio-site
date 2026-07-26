from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_content_handoff.py"


def approved_package() -> dict:
    return {
        "schema_version": 1,
        "source_facts": {
            "basics": [{"id": "fact-1", "value": "Product designer"}],
            "work": [],
            "education": [],
            "projects": [],
            "skills": [],
            "links": [],
        },
        "evidence": [{"id": "evidence-1", "source": "resume.pdf"}],
        "open_questions": [],
        "approved_copy": {
            "summary": {
                "text": "Product designer",
                "approval_status": "user_approved",
                "fact_ids": ["fact-1"],
            }
        },
        "handoff": {
            "status": "approved",
            "revision": 2,
            "source_hashes": ["a" * 64],
        },
    }


def write_handoff(root: Path, package: dict) -> None:
    input_dir = root / ".resume-site-work" / "input"
    reports_dir = root / ".resume-site-work" / "reports"
    input_dir.mkdir(parents=True)
    reports_dir.mkdir(parents=True)
    (input_dir / "source-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_hashes": package["handoff"]["source_hashes"],
            }
        ),
        encoding="utf-8",
    )
    (input_dir / "normalized-resume.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_facts": package["source_facts"],
                "evidence": package["evidence"],
            }
        ),
        encoding="utf-8",
    )
    (input_dir / "approved-copy.json").write_text(
        json.dumps(package), encoding="utf-8"
    )
    (reports_dir / "content-provenance.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "package_revision": package["handoff"]["revision"],
                "package_hash": "b" * 64,
                "evidence_count": len(package["evidence"]),
            }
        ),
        encoding="utf-8",
    )


class ContentHandoffValidatorTests(unittest.TestCase):
    def run_validator(self, workspace: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--workspace-root",
                str(workspace),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_missing_package_requires_content_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_validator(Path(temp_dir))
        self.assertEqual(result.returncode, 2)
        self.assertIn("ROUTE_REQUIRED", result.stdout)

    def test_accepts_an_approved_consistent_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            write_handoff(workspace, approved_package())
            result = self.run_validator(workspace)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CONTENT_READY", result.stdout)

    def test_unapproved_package_requires_content_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            package = approved_package()
            package["handoff"]["status"] = "draft"
            write_handoff(workspace, package)
            result = self.run_validator(workspace)
        self.assertEqual(result.returncode, 2)
        self.assertIn("ROUTE_REQUIRED", result.stdout)

    def test_rejects_normalized_fact_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            write_handoff(workspace, approved_package())
            normalized_path = (
                workspace
                / ".resume-site-work"
                / "input"
                / "normalized-resume.json"
            )
            normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
            normalized["source_facts"]["basics"][0]["value"] = "Changed without approval"
            normalized_path.write_text(json.dumps(normalized), encoding="utf-8")
            result = self.run_validator(workspace)
        self.assertEqual(result.returncode, 1)
        self.assertIn("source_facts mismatch", result.stdout)

    def test_rejects_unapproved_copy_blocks_in_an_approved_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            package = approved_package()
            package["approved_copy"]["summary"]["approval_status"] = "draft"
            write_handoff(workspace, package)
            result = self.run_validator(workspace)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not user_approved", result.stdout)


if __name__ == "__main__":
    unittest.main()
