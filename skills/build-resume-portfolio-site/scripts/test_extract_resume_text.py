from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from extract_resume_text import extract, main


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


if __name__ == "__main__":
    unittest.main()
