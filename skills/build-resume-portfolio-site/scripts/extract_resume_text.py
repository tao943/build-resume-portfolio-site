"""Deterministically extract text from a local resume source."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from xml.etree import ElementTree
from pathlib import Path


IMAGE_FORMATS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def _text_diagnostics(text: str, page_number: int) -> list[dict]:
    if not text.strip():
        return [{"page": page_number, "code": "no_text", "message":
                 "No text extracted: this page may be scanned, blank, or unsupported. Inspect the original page."}]
    suspicious = sum(char == "\ufffd" or unicodedata.category(char) in {"Co", "Cc"}
                     for char in text if char not in "\n\r\t")
    if suspicious >= 2 or re.search(r"\(cid:\d+\)", text):
        return [{"page": page_number, "code": "possible_garbled_text", "message":
                 "Text contains replacement, private-use, control, or unmapped PDF glyphs; compare it with the page."}]
    return []


def _possible_columns(words: list[dict], width: float) -> bool:
    """Flag repeated wide within-line gaps, without claiming a correct reading order."""
    rows: list[list[dict]] = []
    for word in sorted(words, key=lambda value: (float(value["top"]), float(value["x0"]))):
        if rows and abs(float(word["top"]) - float(rows[-1][0]["top"])) <= 4:
            rows[-1].append(word)
        else:
            rows.append([word])
    gaps = []
    for row in rows:
        row.sort(key=lambda value: float(value["x0"]))
        for left, right in zip(row, row[1:]):
            start, end = float(left["x1"]), float(right["x0"])
            if end - start >= width * 0.08 and width * 0.20 < (start + end) / 2 < width * 0.80:
                gaps.append((start, end))
    # A stable gutter on at least three rows is a review signal, not a layout classifier.
    return any(sum(start <= point <= end for start, end in gaps) >= 3
               for point in ((start + end) / 2 for start, end in gaps))


def _ocr_image(path: Path, language: str) -> str:
    executable = shutil.which("tesseract")
    if not executable:
        raise RuntimeError("Local OCR needs Tesseract and the requested language data; install them locally or provide readable text")
    try:
        completed = subprocess.run([executable, str(path), "stdout", "-l", language],
                                   capture_output=True, text=True, encoding="utf-8", timeout=120, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Local OCR timed out; crop the page or provide readable text") from exc
    if completed.returncode:
        raise RuntimeError("Local OCR failed; check image readability and installed language data with tesseract --list-langs")
    return completed.stdout.strip()


def _ocr_pdf_page(path: Path, page_number: int, language: str) -> str:
    renderer = shutil.which("pdftoppm")
    if not renderer:
        raise RuntimeError("Scanned PDF OCR needs local pdftoppm (Poppler); provide page images or install Poppler locally")
    with tempfile.TemporaryDirectory(prefix="resume-ocr-") as temporary:
        output = Path(temporary) / "page"
        try:
            result = subprocess.run([renderer, "-f", str(page_number), "-l", str(page_number),
                                     "-singlefile", "-scale-to", "2000", "-png", str(path), str(output)],
                                    capture_output=True, timeout=90, check=False)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Rendering PDF page {page_number} for local OCR timed out") from exc
        if result.returncode or not output.with_suffix(".png").is_file():
            raise RuntimeError(f"Cannot render PDF page {page_number} for local OCR")
        return _ocr_image(output.with_suffix(".png"), language)


def _extract_pdf(path: Path, ocr: bool = False, language: str = "eng") -> tuple[str, list[str], list[dict]]:
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError(
            "PDF extraction needs pdfplumber in the current Python environment; "
            "see references/import-guide.md for a local virtual environment, or provide readable text"
        ) from exc
    pages: list[str] = []
    diagnostics: list[dict] = []
    try:
        with pdfplumber.open(path) as pdf:
            for number, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                findings = _text_diagnostics(text, number)
                if _possible_columns(page.extract_words() or [], float(page.width)):
                    findings.append({"page": number, "code": "possible_columns", "message":
                                     "Repeated column-like gaps detected; confirm paragraph and date order against this page."})
                if ocr and any(item["code"] in {"no_text", "possible_garbled_text"} for item in findings):
                    text = _ocr_pdf_page(path, number, language)
                    findings.append({"page": number, "code": "ocr_review", "message":
                                     "Local OCR was used. Verify names, dates, links, and numbers against the original; no confidence score is assumed."})
                    if not text.strip():
                        findings.append({"page": number, "code": "ocr_no_text", "message": "Local OCR returned no text."})
                pages.append(text)
                diagnostics.extend(findings)
    except (RuntimeError, OSError):
        raise
    except Exception as exc:
        raise ValueError("Cannot read PDF; it may be damaged, encrypted, or use unsupported text encoding") from exc
    if not pages:
        diagnostics.append({"page": None, "code": "no_pages", "message": "The PDF has no readable pages."})
    return "\n".join(pages).strip(), pages, diagnostics


def _extract_docx(path: Path) -> tuple[str, list[str]]:
    # Word stores table cells, hyperlinks, and text boxes in the same XML tree.
    # Walking paragraphs in document order retains them without python-docx.
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    try:
        with zipfile.ZipFile(path) as document:
            info = document.getinfo("word/document.xml")
            if info.file_size > 20 * 1024 * 1024:
                raise ValueError("DOCX document XML exceeds the 20 MB extraction limit")
            xml = document.read(info)
        if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
            raise ValueError("DOCX XML document types and entities are unsupported")
        tree = ElementTree.fromstring(xml)
        body = tree.find(f"{ns}body")
        if body is None:
            raise ValueError("DOCX has no readable document body")
        def walk(element: ElementTree.Element) -> None:
            if element.tag in {f"{ns}del", f"{ns}moveFrom"}:
                return
            if element.tag == f"{ns}p":
                text: list[str] = []
                def inline(node: ElementTree.Element) -> None:
                    if node.tag in {f"{ns}del", f"{ns}moveFrom"}:
                        return
                    if node.tag == f"{ns}t":
                        text.append(node.text or "")
                    elif node.tag == f"{ns}tab":
                        text.append("\t")
                    elif node.tag in {f"{ns}br", f"{ns}cr"}:
                        text.append("\n")
                    else:
                        for child in node:
                            inline(child)
                inline(element)
                value = "".join(text).strip()
                if value:
                    paragraphs.append(value)
                return
            for child in element:
                walk(child)
        walk(body)
    except (zipfile.BadZipFile, KeyError, ElementTree.ParseError) as exc:
        raise ValueError(f"Cannot read DOCX document: {exc}") from exc
    text = "\n".join(paragraphs)
    return text, [text]


def extract(path: Path, *, ocr: bool = False, ocr_language: str = "eng") -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_]+(?:\+[A-Za-z0-9_]+)*", ocr_language):
        raise ValueError("OCR language must be a Tesseract language code such as eng or chi_sim+eng")
    path = path.resolve()
    suffix = path.suffix.lower()
    diagnostics: list[dict] = []
    method = "text"
    if suffix == ".pdf":
        text, pages, diagnostics = _extract_pdf(path, ocr, ocr_language)
        method = "pdfplumber+local_ocr" if any(item["code"] == "ocr_review" for item in diagnostics) else "pdfplumber"
    elif suffix == ".docx":
        text, pages = _extract_docx(path)
        method = "docx_xml"
    elif suffix in {".md", ".txt"}:
        text = path.read_text(encoding="utf-8-sig")
        pages = [text]
    elif suffix in IMAGE_FORMATS:
        text = _ocr_image(path, ocr_language) if ocr else ""
        pages = [text]
        method = "local_ocr" if ocr else "image_not_extracted"
        diagnostics.append({"page": 1, "code": "ocr_review" if ocr else "image_requires_ocr", "message":
                            "Verify OCR names, dates, links, and numbers against the image." if ocr else
                            "Image input requires native image reading or explicitly enabled local OCR (--ocr); no text was inferred."})
    else:
        raise ValueError(f"Unsupported resume format: {suffix or '<none>'}")

    if suffix != ".pdf":
        diagnostics.extend(_text_diagnostics(text, 1))
    raw = path.read_bytes()
    return {
        "schema_version": 1,
        "source_file": str(path.resolve()),
        "source_hash": hashlib.sha256(raw).hexdigest(),
        "mime_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        "pages": pages,
        "text": text,
        "extraction_method": method,
        "status": "review_required" if diagnostics else "ready",
        "page_diagnostics": diagnostics,
        "warnings": [f"Page {item['page']}: {item['message']}" for item in diagnostics],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ocr", action="store_true", help="Explicitly enable local OCR for images and unreadable PDF pages")
    parser.add_argument("--ocr-language", default="eng", help="Installed Tesseract language code, e.g. chi_sim+eng")
    args = parser.parse_args(argv)
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Extraction output must not replace its source document")
        result = extract(args.input, ocr=args.ocr, ocr_language=args.ocr_language)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if result["status"] == "review_required":
        print("review_required: inspect page_diagnostics before using this extraction as resume facts", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
