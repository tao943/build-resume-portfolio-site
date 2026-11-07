from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from create_demo_workspace import create_workspace, fixture
from manage_resume_versions import save_version, list_versions, compare_versions, select_version, load_version
from write_resume_site_input import write_input
from validate_content_handoff import validate_workspace


class VersionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "master"
        self.role = Path(self.temp.name) / "role"
        create_workspace(self.root)
        create_workspace(self.role, role=True)

    def test_save_compare_select_preserves_master_and_evidence(self):
        original = (self.root / ".resume-site-work/input/approved-copy.json").read_bytes()
        save_version(self.root, self.root, "general")
        save_version(self.root, self.role, "frontend", "前端岗位")
        diff = compare_versions(self.root, "general", "frontend")
        summary = next(row for row in diff["changes"] if row["block_id"] == "summary")
        self.assertNotEqual(summary["before"], summary["after"])
        self.assertEqual(len(diff["changes"]), 1)
        self.assertEqual(summary["evidence"][0]["evidence_id"], "evidence-summary")
        self.assertEqual(diff["gaps"][0]["id"], "mentoring")
        selected = select_version(self.root, "frontend")
        self.assertTrue((Path(selected["workspace"]) / ".resume-site-work/input/approved-copy.json").exists())
        self.assertEqual(len(list_versions(self.root)), 2)
        self.assertEqual(original, (self.root / ".resume-site-work/input/approved-copy.json").read_bytes())

    def test_rejects_changed_facts_overwrite_and_path_traversal(self):
        save_version(self.root, self.root, "general")
        with self.assertRaises(FileExistsError):
            save_version(self.root, self.root, "general")
        with self.assertRaises(ValueError):
            save_version(self.root, self.role, "../escape")
        for name in ("approved-copy", "normalized-resume"):
            path = self.role / f".resume-site-work/input/{name}.json"
            data = json.loads(path.read_text())
            data["source_facts"]["basics"]["name"]["value"] = "different person"
            path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "preserve"):
            save_version(self.root, self.role, "frontend")

    def test_rejects_drift_and_unknown_fact_references(self):
        save_version(self.root, self.root, "general")
        selected = select_version(self.root, "general")
        path = Path(selected["workspace"]) / ".resume-site-work/input/approved-copy.json"
        path.write_text(path.read_text() + " ")
        with self.assertRaisesRegex(ValueError, "changed"):
            load_version(self.root, "general")
        package_path = self.role / ".resume-site-work/input/approved-copy.json"
        quality_path = self.role / ".resume-site-work/reports/content-quality-review.json"
        package, quality = json.loads(package_path.read_text()), json.loads(quality_path.read_text())
        package["approved_copy"]["summary"]["fact_ids"] = ["fact-invented"]
        next(row for row in quality["blocks"] if row["block_id"] == "summary")["fact_ids"] = ["fact-invented"]
        package_path.write_text(json.dumps(package)); quality_path.write_text(json.dumps(quality))
        with self.assertRaisesRegex(ValueError, "unknown fact"):
            save_version(self.root, self.role, "frontend")

    def test_writer_uses_portable_paths_and_preserves_revision(self):
        self.assertTrue((self.root / ".resume-site-work/reports/content-provenance.json").exists())
        package, _, _ = fixture()
        source = self.root / "new.json"
        source.write_text(json.dumps(package))
        with self.assertRaises(ValueError):
            write_input(source, self.root, revision=1)
        write_input(source, self.root, revision=2)
        snapshot_root = self.root / ".resume-site-work/versions/content-r1"
        snapshot = snapshot_root / ".resume-site-work/input/approved-copy.json"
        self.assertEqual(json.loads(snapshot.read_text())["handoff"]["revision"], 1)
        self.assertEqual(validate_workspace(snapshot_root)[0], 0)

    def staged_role(self):
        package, quality, jd = fixture(role=True)
        paths = []
        for name, value in (("package", package), ("quality", quality), ("jd", jd)):
            path = self.root / f"staged-{name}.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            paths.append(path)
        return paths

    def handoff_bytes(self):
        work = self.root / ".resume-site-work"
        return {str(path.relative_to(work)): path.read_bytes() for path in work.rglob("*") if path.is_file()}

    def test_writer_stages_role_report_and_restores_valid_old_snapshot(self):
        before = self.handoff_bytes()
        package, quality, jd = self.staged_role()
        write_input(package, self.root, revision=2, quality_review_path=quality, jd_report_path=jd)
        snapshot = self.root / ".resume-site-work/versions/content-r1"
        self.assertEqual(validate_workspace(self.root)[0], 0)
        self.assertEqual(validate_workspace(snapshot)[0], 0)
        for relative, raw in before.items():
            self.assertEqual((snapshot / ".resume-site-work" / relative).read_bytes(), raw)
        old_copy = json.loads((snapshot / ".resume-site-work/input/approved-copy.json").read_text())
        new_copy = json.loads((self.root / ".resume-site-work/input/approved-copy.json").read_text())
        self.assertNotEqual(old_copy["approved_copy"]["summary"]["text"], new_copy["approved_copy"]["summary"]["text"])

    def test_writer_invalid_candidate_never_changes_existing_handoff(self):
        before = self.handoff_bytes()
        package, quality, jd = self.staged_role()
        review = json.loads(quality.read_text())
        review["blocks"][0]["recommended_copy"] = "Unapproved replacement"
        quality.write_text(json.dumps(review))
        with self.assertRaisesRegex(ValueError, "New staged handoff is invalid"):
            write_input(package, self.root, revision=2, quality_review_path=quality, jd_report_path=jd)
        self.assertEqual(self.handoff_bytes(), before)

    def test_writer_rejects_already_replaced_old_report(self):
        package, quality, jd = self.staged_role()
        (self.root / ".resume-site-work/reports/content-quality-review.json").write_bytes(quality.read_bytes())
        before = self.handoff_bytes()
        with self.assertRaisesRegex(ValueError, "stage new reports elsewhere"):
            write_input(package, self.root, revision=2, quality_review_path=quality, jd_report_path=jd)
        self.assertEqual(self.handoff_bytes(), before)

    def test_writer_write_failure_rolls_back_all_files(self):
        before = self.handoff_bytes()
        package, quality, jd = self.staged_role()
        original_replace = Path.replace
        def fail_quality_once(source, target):
            if Path(target).name == "content-quality-review.json":
                raise OSError("Simulated write failure")
            return original_replace(source, target)
        with patch("write_resume_site_input.Path.replace", new=fail_quality_once):
            with self.assertRaisesRegex(OSError, "Simulated write failure"):
                write_input(package, self.root, revision=2, quality_review_path=quality, jd_report_path=jd)
        self.assertEqual(self.handoff_bytes(), before)
        self.assertEqual(validate_workspace(self.root)[0], 0)

    def test_rejects_unknown_stronger_evidence(self):
        save_version(self.root, self.root, "general")
        path = self.role / ".resume-site-work/reports/content-quality-review.json"
        review = json.loads(path.read_text())
        summary = next(row for row in review["blocks"] if row["block_id"] == "summary")
        summary["selected_version"] = "stronger"
        summary["stronger_version"] = {"copy": summary["recommended_copy"], "fact_ids": summary["fact_ids"],
                                       "evidence_ids": ["evidence-missing"]}
        path.write_text(json.dumps(review))
        with self.assertRaisesRegex(ValueError, "unknown facts/evidence"):
            save_version(self.root, self.role, "frontend")

    def test_compare_uses_selected_stronger_and_removed_block_evidence(self):
        save_version(self.root, self.root, "general")
        quality_path = self.role / ".resume-site-work/reports/content-quality-review.json"
        package_path = self.role / ".resume-site-work/input/approved-copy.json"
        review, package = json.loads(quality_path.read_text()), json.loads(package_path.read_text())
        summary = next(row for row in review["blocks"] if row["block_id"] == "summary")
        summary["selected_version"] = "stronger"
        summary["stronger_version"] = {"copy": summary["recommended_copy"], "fact_ids": summary["fact_ids"],
                                       "evidence_ids": ["evidence-work"]}
        package["approved_copy"].pop("contact")
        review["blocks"] = [row for row in review["blocks"] if row["block_id"] != "contact"]
        review["copy_approval"]["approved_block_ids"].remove("contact")
        quality_path.write_text(json.dumps(review))
        package_path.write_text(json.dumps(package))
        save_version(self.root, self.role, "frontend")
        changes = {row["block_id"]: row for row in compare_versions(self.root, "general", "frontend")["changes"]}
        self.assertEqual([row["evidence_id"] for row in changes["summary"]["evidence"]], ["evidence-work"])
        self.assertEqual(changes["contact"]["change"], "removed")
        self.assertEqual([row["evidence_id"] for row in changes["contact"]["evidence"]], ["evidence-contact"])


if __name__ == "__main__":
    unittest.main()
