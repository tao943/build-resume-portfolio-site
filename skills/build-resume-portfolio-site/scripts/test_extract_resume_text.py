from __future__ import annotations

import tempfile
import json
import types
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from extract_resume_text import extract, main, _possible_columns, _ocr_image
from normalize_resume_sources import normalize


class ResumeExtractionTests(unittest.TestCase):
    def test_docx_preserves_body_table_hyperlink_and_unicode_in_order(self):
        xml = '''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
        <w:body><w:p><w:r><w:t>陈同学</w:t></w:r></w:p>
        <w:tbl><w:tr><w:tc><w:p><w:r><w:t>项目 A</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>React</w:t><w:tab/><w:t>Vite</w:t></w:r>
        <w:hyperlink><w:r><w:t>作品链接</w:t></w:r></w:hyperlink></w:p></w:tc></w:tr></w:tbl>
        <w:p><w:del><w:r><w:delText>旧指标 200%</w:delText></w:r></w:del>
        <w:r><w:t>待核实成果</w:t><w:br/><w:t>不补造指标</w:t></w:r></w:p></w:body></w:document>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "简历.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", xml)
            result = extract(path)
        self.assertEqual(result["text"], "陈同学\n项目 A\nReact\tVite作品链接\n待核实成果\n不补造指标")
        self.assertEqual(result["pages"], [result["text"]])
        self.assertEqual(len(result["source_hash"]), 64)

    def test_utf8_bom_is_not_a_resume_character(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "resume.txt"
            path.write_bytes(b"\xef\xbb\xbf" + "测试简历".encode())
            self.assertEqual(extract(path)["text"], "测试简历")

    def test_broken_docx_returns_error_without_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / "broken.docx", Path(tmp) / "result.json"
            source.write_bytes(b"not a ZIP")
            self.assertEqual(main(["--input", str(source), "--output", str(output)]), 1)
            self.assertFalse(output.exists())

    def test_rejects_entity_declarations(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "entity.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", '<!DOCTYPE x [<!ENTITY a "secret">]><x>&a;</x>')
            with self.assertRaisesRegex(ValueError, "entities are unsupported"):
                extract(path)

    def test_empty_text_writes_review_report_and_non_success_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / "empty.txt", Path(tmp) / "report.json"
            source.write_text("\n", encoding="utf-8")
            self.assertEqual(main(["--input", str(source), "--output", str(output)]), 2)
            report = json.loads(output.read_text())
        self.assertEqual(report["status"], "review_required")
        self.assertEqual(report["page_diagnostics"][0]["code"], "no_text")

    def test_scanned_and_garbled_pdf_report_actual_page_numbers(self):
        class Page:
            width = 600
            def __init__(self, text):
                self.text = text
            def extract_text(self):
                return self.text
            def extract_words(self):
                return []
        pdf = types.SimpleNamespace(pages=[Page("Normal resume text"), Page(""), Page("(cid:23) \ufffd\ufffd")])
        context = unittest.mock.MagicMock()
        context.__enter__.return_value = pdf
        module = types.SimpleNamespace(open=lambda path: context)
        with tempfile.TemporaryDirectory() as tmp, patch.dict("sys.modules", {"pdfplumber": module}):
            source = Path(tmp) / "mixed.pdf"
            source.write_bytes(b"fake fixture; reader supplied by test")
            report = extract(source)
        self.assertEqual(report["pages"], ["Normal resume text", "", "(cid:23) \ufffd\ufffd"])
        self.assertEqual([(item["page"], item["code"]) for item in report["page_diagnostics"]],
                         [(2, "no_text"), (3, "possible_garbled_text")])

    def test_column_heuristic_requires_repeated_gutter(self):
        words = []
        for y in (10, 30, 50):
            words.extend([{"x0": 20, "x1": 180, "top": y}, {"x0": 340, "x1": 500, "top": y}])
        self.assertTrue(_possible_columns(words, 600))
        self.assertFalse(_possible_columns(words[:2], 600))
        self.assertFalse(_possible_columns([{"x0": 20, "x1": 550, "top": y} for y in (10, 30, 50)], 600))

    def test_images_need_explicit_ocr_and_enter_source_manifest(self):
        with tempfile.TemporaryDirectory() as tmp, patch("extract_resume_text._ocr_image") as ocr:
            source = Path(tmp) / "resume.png"
            source.write_bytes(b"fixture")
            report = extract(source)
            ocr.assert_not_called()
            self.assertEqual(report["text"], "")
            self.assertEqual(report["status"], "review_required")
            self.assertEqual(normalize(Path(tmp))["sources"][0]["extension"], ".png")
            ocr.return_value = "陈同学 2025"
            report = extract(source, ocr=True, ocr_language="chi_sim+eng")
            ocr.assert_called_once_with(source.resolve(), "chi_sim+eng")
            self.assertEqual(report["text"], "陈同学 2025")
            self.assertEqual(report["status"], "review_required")

    def test_corrupt_pdf_returns_actionable_error(self):
        def fail(path):
            raise Exception("parser implementation detail")
        with tempfile.TemporaryDirectory() as tmp, patch.dict("sys.modules", {"pdfplumber": types.SimpleNamespace(open=fail)}):
            source = Path(tmp) / "broken.pdf"
            source.write_bytes(b"bad pdf")
            with self.assertRaisesRegex(ValueError, "damaged, encrypted"):
                extract(source)

    def test_pdf_ocr_only_retries_unreadable_pages(self):
        class Page:
            width = 600
            def __init__(self, text):
                self.text = text
            def extract_text(self):
                return self.text
            def extract_words(self):
                return []
        context = unittest.mock.MagicMock()
        context.__enter__.return_value = types.SimpleNamespace(pages=[Page("Keep readable page"), Page("")])
        module = types.SimpleNamespace(open=lambda path: context)
        with tempfile.TemporaryDirectory() as tmp, patch.dict("sys.modules", {"pdfplumber": module}), \
                patch("extract_resume_text._ocr_pdf_page", return_value="Recognized second page") as ocr:
            source = Path(tmp) / "mixed.pdf"
            source.write_bytes(b"fixture")
            report = extract(source, ocr=True)
            ocr.assert_called_once_with(source.resolve(), 2, "eng")
        self.assertEqual(report["pages"], ["Keep readable page", "Recognized second page"])
        self.assertEqual(report["status"], "review_required")
        self.assertEqual(report["extraction_method"], "pdfplumber+local_ocr")

    def test_missing_local_ocr_has_actionable_error(self):
        with patch("extract_resume_text.shutil.which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "Tesseract"):
                _ocr_image(Path("resume.png"), "eng")

    def test_output_cannot_overwrite_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "resume.txt"
            source.write_text("Keep this resume", encoding="utf-8")
            self.assertEqual(main(["--input", str(source), "--output", str(source)]), 1)
            self.assertEqual(source.read_text(), "Keep this resume")


class RealPdfExtractionTests(unittest.TestCase):
    def test_real_pdf_retains_pages_and_flags_dual_columns(self):
        try:
            import pdfplumber  # noqa: F401
            from reportlab.pdfgen.canvas import Canvas
        except ImportError:
            self.skipTest("optional pdfplumber/reportlab are not installed")
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "columns.pdf"
            canvas = Canvas(str(source), pagesize=(600, 800))
            for y, left, right in [(720, "Experience", "Skills"), (690, "Frontend Engineer", "React and Vite"),
                                   (660, "Built dashboards", "Accessible interfaces")]:
                canvas.drawString(30, y, left)
                canvas.drawString(340, y, right)
            canvas.showPage()
            canvas.showPage()
            canvas.save()
            report = extract(source)
        self.assertEqual(len(report["pages"]), 2)
        self.assertIn("Experience", report["pages"][0])
        self.assertIn((1, "possible_columns"), [(item["page"], item["code"]) for item in report["page_diagnostics"]])
        self.assertIn((2, "no_text"), [(item["page"], item["code"]) for item in report["page_diagnostics"]])


if __name__ == "__main__":
    unittest.main()
