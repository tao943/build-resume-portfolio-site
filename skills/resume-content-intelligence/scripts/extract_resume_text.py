"""Deterministically extract text from a local resume source."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import sys
from pathlib import Path


def _extract_pdf(path: Path) -> tuple[str, list[str]]:
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("PDF extraction requires pdfplumber") from exc
    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages).strip(), pages


def _extract_docx(path: Path) -> tuple[str, list[str]]:
    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError("DOCX extraction requires python-docx") from exc
    paragraphs = [p.text.strip() for p in Document(path).paragraphs if p.text.strip()]
    text = "\n".join(paragraphs)
    return text, [text]


def extract(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text, pages = _extract_pdf(path)
    elif suffix == ".docx":
        text, pages = _extract_docx(path)
    elif suffix in {".md", ".txt"}:
        text = path.read_text(encoding="utf-8")
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
        "warnings": ["No extractable text found"] if not text.strip() else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
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
