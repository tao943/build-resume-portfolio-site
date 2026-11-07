"""Behavioral tests for approved-content export, without personal resume data."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import export_resume as export
from validate_content_quality_review import ATS_CHECKS, INTEGRITY_CHECKS


def fixture(language="zh", long=False):
    texts = {
        "name": "林知远" if language == "zh" else "Alex Example",
        "contact": "alex@example.invalid | https://example.com/portfolio",
        "summary": "软件工程师，关注可访问性与前端交付。" if language == "zh" else "Software engineer focused on accessible interfaces.",
        "work": "负责交互组件实现，使用 React 与 TypeScript 完成可访问性改进。" if language == "zh" else "Built accessible React components with TypeScript.",
    }
    if long:
        for index in range(60):
            texts[f"project-{index}"] = f"Project {index:02}: Built a documented prototype, tested keyboard navigation, and recorded the results. " * 3
    facts = {key: {"fact_id": "fact-" + key, "value": text, "source_ids": ["source-example"],
                   "confidence": "high", "confirmation_status": "user_confirmed"}
             for key, text in texts.items()}
    package = {
        "schema_version": 1,
        "source_facts": {"basics": facts, "work": [], "education": [], "projects": [], "skills": [], "links": []},
        "evidence": [{"evidence_id": "evidence-example", "source_id": "source-example",
                      "quote": "Fictional test fixture; no actual user approval.", "location": "test"}],
        "open_questions": [],
        "approved_copy": {key: {"text": text, "fact_ids": ["fact-" + key], "version": 1,
                                 "approval_status": "user_approved"} for key, text in texts.items()},
        "handoff": {"status": "approved", "revision": 1, "source_hashes": []},
    }
    plan = {"schema_version": 1, "package_revision": 1, "package_sha256": export.package_digest(package),
            "language": language, "audience": "private", "title_block_id": "name",
            "contact_block_ids": ["contact"],
            "sections": [{"kind": "summary", "block_ids": ["summary"]},
                         {"kind": "work", "block_ids": ["work"]}]}
    if long:
        plan["sections"].append({"kind": "projects", "block_ids": [f"project-{index}" for index in range(60)]})
    return package, plan


def write_workspace(root, package):
    """Build an honest synthetic handoff to exercise the real boundary validator."""
    blocks = []
    for key, block in package["approved_copy"].items():
        blocks.append({"block_id": key, "source_section": "basics", "original_copy": block["text"],
                       "recommended_copy": block["text"], "stronger_version": None,
                       "selected_version": "recommended", "action": "Provided fictional copy",
                       "method": "Synthetic test", "scope": "Test fixture only",
                       "result": {"kind": "qualitative_fallback", "text": block["text"],
                                  "fact_ids": [], "evidence_ids": [], "reason": "No invented metrics",
                                  "unsupported_metrics_removed": True},
                       "fact_ids": block["fact_ids"], "evidence_ids": ["evidence-example"],
                       "jd_requirement_ids": [], "integrity_review": dict.fromkeys(INTEGRITY_CHECKS, True),
                       "approval_status": block["approval_status"]})
    quality = {"schema_version": 1, "review_status": "approved",
               "jd_review": {"present": False, "matched_requirement_ids": [], "unmatched_requirement_ids": []},
               "ats_review": {**dict.fromkeys(ATS_CHECKS, True), "notes": []}, "blocked_claims": [],
               "blocks": blocks, "copy_approval": {"status": "user_approved", "source": "conversation",
                "approved_block_ids": list(package["approved_copy"]),
                "evidence_quote": "Simulated approval for fictional software tests, not a real user."}}
    payloads = {
        "input/approved-copy.json": package,
        "input/source-manifest.json": {"schema_version": 1, "source_hashes": []},
        "input/normalized-resume.json": {"schema_version": 1, "source_facts": package["source_facts"],
                                         "evidence": package["evidence"]},
        "reports/content-provenance.json": {"schema_version": 1, "package_revision": 1,
                                            "package_hash": export.package_digest(package), "evidence_count": 1},
        "reports/content-quality-review.json": quality,
    }
    for relative, payload in payloads.items():
        path = root / ".resume-site-work" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class ExportPlanTests(unittest.TestCase):
    def test_rejects_draft_copy_and_stale_plan(self):
        package, plan = fixture()
        package["approved_copy"]["work"]["approval_status"] = "draft"
        plan["package_sha256"] = export.package_digest(package)
        with self.assertRaisesRegex(ValueError, "unapproved"):
            export.document_from_plan(package, plan)
        package, plan = fixture()
        package["approved_copy"]["work"]["text"] += " Changed"
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            export.document_from_plan(package, plan)

    def test_public_export_requires_exact_public_approval(self):
        package, plan = fixture()
        plan["audience"] = "public"
        with self.assertRaises(ValueError):
            export.document_from_plan(package, plan)
        plan["public_approval"] = {"status": "user_approved", "source": "conversation",
                                   "evidence_quote": "Fictional public test approval",
                                   "block_ids": ["name", "contact", "summary"]}
        with self.assertRaises(ValueError):
            export.document_from_plan(package, plan)
        plan["public_approval"]["block_ids"].append("work")
        self.assertEqual(export.document_from_plan(package, plan)["audience"], "public")

    def test_hidden_facts_and_unselected_blocks_never_leak(self):
        package, plan = fixture()
        package["source_facts"]["basics"]["private_phone"] = {"value": "PRIVATE-PHONE-SECRET"}
        package["approved_copy"]["private_contact"] = {"text": "PRIVATE-EMAIL-SECRET", "fact_ids": ["fact-contact"],
                                                        "version": 1, "approval_status": "user_approved"}
        plan["package_sha256"] = export.package_digest(package)
        rendered = json.dumps(export.document_from_plan(package, plan))
        self.assertNotIn("SECRET", rendered)

    def test_html_is_escaped_and_links_only_visible_urls(self):
        text = '<script>alert("x")</script> <img src="secret"> https://example.com/a?b=1&c=2'
        marked = export.marked_text(text)
        self.assertNotIn("<script>", marked)
        self.assertNotIn("<img", marked)
        self.assertIn("&lt;script&gt;", marked)
        self.assertIn('href="https://example.com/a?b=1&amp;c=2"', marked)
        self.assertNotIn("href", export.marked_text("javascript:alert(1) data:text/html,evil"))

    def test_full_handoff_gate_and_no_overwrite(self):
        package, plan = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "exports/v1"
            with self.assertRaisesRegex(ValueError, "not ready"):
                export.export_resume(root, plan, output, "html")
            write_workspace(root, package)
            report = export.export_resume(root, plan, output, "html")
            self.assertEqual(set(report["files"]), {"resume.html"})
            self.assertIn("林知远", (output / "resume.html").read_text())
            with self.assertRaises(FileExistsError):
                export.export_resume(root, plan, output, "html")
            with self.assertRaisesRegex(ValueError, "outside the site"):
                export.export_resume(root, plan, root / ".resume-site-work/site/public/export", "html")

    def test_changed_reviewed_copy_cannot_be_exported(self):
        package, plan = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_workspace(root, package)
            package["approved_copy"]["work"]["text"] += " Unsupported added claim"
            plan["package_sha256"] = export.package_digest(package)
            (root / ".resume-site-work/input/approved-copy.json").write_text(json.dumps(package))
            with self.assertRaisesRegex(ValueError, "does not match approved reviewed copy"):
                export.export_resume(root, plan, root / "export", "html")


@unittest.skipUnless(importlib.util.find_spec("reportlab") and importlib.util.find_spec("pypdf"),
                     "optional PDF dependencies reportlab and pypdf are not installed")
class PDFExportTests(unittest.TestCase):
    def test_missing_font_fails_without_partial_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            package, plan = fixture()
            root = Path(temporary)
            write_workspace(root, package)
            with self.assertRaisesRegex(ValueError, "embeddable TrueType font"):
                export.export_resume(root, plan, root / "export", font_path=root / "missing.ttf")
            self.assertFalse((root / "export").exists())
            self.assertFalse(list(root.glob(".resume-export-*")))

    def test_chinese_english_pdf_keeps_text_and_links(self):
        from pypdf import PdfReader
        for language in ("zh", "en"):
            with self.subTest(language=language), tempfile.TemporaryDirectory() as temporary:
                package, plan = fixture(language)
                root = Path(temporary)
                write_workspace(root, package)
                report = export.export_resume(root, plan, root / "export")
                self.assertTrue(report["pdf_checks"]["text_order_verified"])
                self.assertEqual(report["pdf_checks"]["page_count"], 1)
                reader = PdfReader(root / "export/resume.pdf")
                text = "".join(page.extract_text() for page in reader.pages)
                self.assertIn(package["approved_copy"]["name"]["text"], text)
                urls = [str(annot.get_object().get("/A", {}).get("/URI", ""))
                        for page in reader.pages for annot in page.get("/Annots", [])]
                self.assertIn("https://example.com/portfolio", urls)

    def test_long_resume_paginates_without_losing_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            package, plan = fixture("en", long=True)
            root = Path(temporary)
            write_workspace(root, package)
            report = export.export_resume(root, plan, root / "export")
            self.assertGreater(report["pdf_checks"]["page_count"], 1)
            self.assertTrue(report["pdf_checks"]["text_order_verified"])


if __name__ == "__main__":
    unittest.main()
