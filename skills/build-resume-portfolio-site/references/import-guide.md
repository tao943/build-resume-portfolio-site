# Local setup and resume import

Use this guide for first-run setup, PDF/image input, or a failed extraction.
Check the actual interpreter and PATH before asking the user to install anything:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/check_environment.py"
```

The check does not install software, upload files, or change the machine. Python
3.10+ and Node.js 22.12+ with npm are the website-generation prerequisites.
Missing Node/npm does not prevent reading or preparing resume text; finish that
work while the website runtime is being prepared. Reuse an available compatible
runtime when the host provides one.

Optional features can be made explicit requirements with repeated `--require`
arguments: `pdf-import`, `pdf-export`, `pdf-audit`, or `ocr`. `ocr` checks
Tesseract; scanned PDF OCR additionally needs `pdf-import` and `pdf-audit`.
Check `ocr_languages` before choosing a language. A capability check is not a
successful build, import, or PDF audit.

## Optional Python packages

DOCX and UTF-8 text need no extra packages. PDF input uses `pdfplumber`; PDF
delivery uses `reportlab` and `pypdf`. Use the user's existing environment, or a
workspace-local virtual environment. These are example setup commands, not
automatic global installation instructions:

```sh
python3 -m venv .resume-site-work/.venv
.resume-site-work/.venv/bin/python -m pip install pdfplumber reportlab pypdf
```

On Windows, use the verified Python 3 executable and
`.resume-site-work/.venv/Scripts/python.exe` instead. Point `PYTHON` at the
environment's Python before checking or importing again. Install only the
packages needed for the chosen features. Poppler (`pdftoppm`) and Tesseract are
optional local system tools; use the platform's normal installation method if
requested. Do not download resume files or send them to an OCR service.

## Extraction and review

```sh
"$PYTHON" "$SKILL_ROOT/scripts/extract_resume_text.py" \
  --input "/absolute/path/resume.pdf" \
  --output ".resume-site-work/reports/extracted-resume.json"
```

- Exit `0`: text extraction is ready for normal fact/evidence review. It does
  not mean that facts, public contact fields, or wording have been approved.
- Exit `2`: a report was written with `status: review_required`. Read its
  `page_diagnostics` and compare the affected pages with the original before
  promoting extracted text to evidence. Preserve the unresolved items as
  questions; do not treat blank text as an empty resume.
- Exit `1`: extraction failed. Read the actionable error and keep the original
  file intact; do not use a previous output as if the latest attempt succeeded.

`pages` retain source page boundaries. `page_diagnostics` identifies pages with
no text, unmapped glyphs, or repeated column-like gaps. The column check is a
heuristic: it can flag tables and can miss unusual layouts. It does not reorder
text or certify reading order. Inspect double-column PDFs, mixed image/text
pages, dates and section boundaries even when the check is quiet. Names,
numbers and dates remain subject to fact confirmation.

## Images and scanned PDFs

PNG, JPEG, TIFF and BMP input without `--ocr` returns a review report so the
agent can use its native image-reading capability or request readable text.
OCR is local and only enabled by the explicit flag, after the user has chosen
that path. For Chinese and English, when both language packs are installed:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/extract_resume_text.py" \
  --input "/absolute/path/scanned-resume.pdf" \
  --output ".resume-site-work/reports/extracted-resume.json" \
  --ocr --ocr-language chi_sim+eng
```

For PDFs, only pages with no usable text or suspicious glyphs are sent through
OCR. Image inputs are read directly by Tesseract. Temporary rendered pages are
removed automatically. OCR output always needs review; no confidence score is
invented. Compare names, dates, URLs and numerical claims with the original.
If tools or language packs are missing, use native reading or a text-readable
copy and record which facts still need confirmation.
