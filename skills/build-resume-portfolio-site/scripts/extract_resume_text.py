"""Deterministically extract text from a local resume source."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import sys
import zipfile
from xml.etree import ElementTree
from pathlib import Path


def _extract_pdf(path: Path) -> tuple[str, list[str]]:
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError(
            "optional PDF helper is unavailable; use native document reading, "
            "a text-readable file, or user transcription"
        ) from exc
    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages).strip(), pages


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


def extract(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text, pages = _extract_pdf(path)
    elif suffix == ".docx":
        text, pages = _extract_docx(path)
    elif suffix in {".md", ".txt"}:
        text = path.read_text(encoding="utf-8-sig")
        pages = [text]
    else:
        raise ValueError(f"Unsupported resume format: {suffix or '<none>'}")

    raw = path.read_bytes()
    return {
        "schema_version": 1,
        "source_file": str(path.resolve()),
        "source_hash": hashlib.sha256(raw).hexdigest(),
        "mime_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        "pages": pages,
        "text": text,
        "warnings": (
            [
                "No extractable text found; use native document reading, a "
                "text-readable file, or user transcription"
            ]
            if not text.strip()
            else []
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = extract(args.input)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
