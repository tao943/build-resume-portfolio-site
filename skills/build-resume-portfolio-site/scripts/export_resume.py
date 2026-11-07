"""Export a validated content handoff as a text PDF and printable HTML.

No source facts, evidence quotes, or private reports are copied into the document.
The layout only selects already approved copy blocks; it cannot rewrite them.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from validate_content_handoff import validate_workspace


HEADINGS = {
    "en": {"summary": "Profile", "work": "Experience", "projects": "Projects",
           "education": "Education", "skills": "Skills", "links": "Links"},
    "zh": {"summary": "个人简介", "work": "工作经历", "projects": "项目经历",
           "education": "教育背景", "skills": "专业技能", "links": "相关链接"},
}
URL_RE = re.compile(r"(?:https?://|mailto:)[^\s<>\"']+")


def package_digest(package: dict) -> str:
    return hashlib.sha256(json.dumps(package, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def _ids(value: object, label: str, allow_empty: bool = False) -> list[str]:
    if (not isinstance(value, list) or (not value and not allow_empty)
            or not all(isinstance(item, str) and item.strip() for item in value)
            or len(value) != len(set(value))):
        raise ValueError(f"{label} must be a unique {'possibly empty ' if allow_empty else ''}string list")
    return value


def document_from_plan(package: dict, plan: dict) -> dict:
    """Resolve a presentation plan without introducing any new resume wording."""
    if not isinstance(package, dict) or not isinstance(plan, dict):
        raise ValueError("package and export plan must be objects")
    handoff = package.get("handoff", {})
    if package.get("schema_version") != 1 or handoff.get("status") != "approved":
        raise ValueError("export requires an approved schema-version-1 content handoff")
    if (plan.get("schema_version") != 1
            or plan.get("package_revision") != handoff.get("revision")
            or plan.get("package_sha256") != package_digest(package)):
        raise ValueError("export plan must match the current package revision and SHA-256")
    language = plan.get("language", "zh")
    audience = plan.get("audience", "private")
    if language not in HEADINGS or audience not in {"private", "public"}:
        raise ValueError("language must be zh/en and audience must be private/public")
    title_id = plan.get("title_block_id")
    if not isinstance(title_id, str) or not title_id.strip():
        raise ValueError("title_block_id must select approved name/title wording")
    contacts = _ids(plan.get("contact_block_ids", []), "contact_block_ids", True)
    sections = plan.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValueError("sections must be a non-empty list")
    ids = [title_id] + contacts
    for index, section in enumerate(sections):
        if not isinstance(section, dict) or section.get("kind") not in HEADINGS[language]:
            raise ValueError(f"sections[{index}].kind is invalid")
        ids.extend(_ids(section.get("block_ids"), f"sections[{index}].block_ids"))
    if len(ids) != len(set(ids)):
        raise ValueError("each approved block may appear only once in the resume")
    blocks = package.get("approved_copy", {})
    if not isinstance(blocks, dict):
        raise ValueError("approved_copy must be an object")
    for block_id in ids:
        block = blocks.get(block_id)
        if (not isinstance(block, dict) or block.get("approval_status") != "user_approved"
                or not isinstance(block.get("text"), str) or not block["text"].strip()
                or not isinstance(block.get("version"), int) or block["version"] < 1):
            raise ValueError(f"{block_id}: missing or unapproved copy")
        _ids(block.get("fact_ids"), f"{block_id}.fact_ids")
        if any(ord(char) < 32 and char not in "\n\t\r" for char in block["text"]):
            raise ValueError(f"{block_id}: unsupported control character")
    if audience == "public":
        approval = plan.get("public_approval", {})
        if (not isinstance(approval, dict) or approval.get("status") != "user_approved"
                or approval.get("source") != "conversation"
                or not isinstance(approval.get("evidence_quote"), str)
                or not approval["evidence_quote"].strip()
                or set(_ids(approval.get("block_ids"), "public_approval.block_ids")) != set(ids)):
            raise ValueError("public export requires conversational approval of exactly its selected blocks")
    text = lambda block_id: blocks[block_id]["text"]
    return {"language": language, "audience": audience, "title": text(title_id),
            "contacts": [text(item) for item in contacts],
            "sections": [{"heading": HEADINGS[language][section["kind"]],
                          "blocks": [text(item) for item in section["block_ids"]]}
                         for section in sections],
            "block_ids": ids, "package_revision": handoff["revision"],
            "package_sha256": package_digest(package)}


def _safe_url(value: str) -> bool:
    parsed = urlsplit(value)
    return ((parsed.scheme in {"http", "https"} and bool(parsed.hostname)
             and not parsed.username and not parsed.password)
            or (parsed.scheme == "mailto" and bool(parsed.path) and not parsed.query))


def marked_text(text: str) -> str:
    """Escape user text first; create links only for visible approved URL strings."""
    parts, start = [], 0
    for match in URL_RE.finditer(text):
        url = match.group().rstrip(".,;!?)，。；！）")
        end = match.start() + len(url)
        parts.append(html.escape(text[start:match.start()]))
        if _safe_url(url):
            parts.append(f'<a href="{html.escape(url, quote=True)}">{html.escape(url)}</a>')
        else:
            parts.append(html.escape(url))
        start = end
    parts.append(html.escape(text[start:]))
    return "".join(parts).replace("\n", "<br/>").replace("\t", "    ")


def write_html(document: dict, target: Path) -> None:
    parts = [f"<h1>{marked_text(document['title'])}</h1>"]
    parts.extend(f'<p class="contact">{marked_text(item)}</p>' for item in document["contacts"])
    for section in document["sections"]:
        parts.append(f'<section><h2>{html.escape(section["heading"])}</h2>')
        parts.extend(f'<p>{marked_text(item)}</p>' for item in section["blocks"])
        parts.append("</section>")
    target.write_text("<!doctype html>\n" + f'<html lang="{document["language"]}"><head>'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow">'
        f'<title>{html.escape(document["title"])}</title><style>'
        '@page{size:A4;margin:18mm}*{box-sizing:border-box}body{max-width:174mm;margin:24px auto;'
        'padding:0 18px;color:#18212b;font:11pt/1.55 "Noto Sans CJK SC","PingFang SC",'
        '"Microsoft YaHei",Arial,sans-serif}h1{font-size:25pt;line-height:1.2;margin:0 0 9px}'
        'h2{font-size:12pt;letter-spacing:.02em;border-bottom:1px solid #9aabb8;'
        'padding-bottom:4px;margin:20px 0 9px;break-after:avoid}p{margin:0 0 10px;'
        'overflow-wrap:anywhere;orphans:3;widows:3}.contact{font-size:10pt;margin:0 0 4px}'
        'a{color:#1f4e68;text-decoration:underline}@media print{body{margin:0;padding:0;'
        'max-width:none}a{color:inherit}}'
        '</style></head><body>' + "\n".join(parts) + '</body></html>\n', encoding="utf-8")


def _all_text(document: dict) -> list[str]:
    result = [document["title"], *document["contacts"]]
    for section in document["sections"]:
        result.extend([section["heading"], *section["blocks"]])
    return result


def _pdf_font(texts: list[str], font_path: Path | None = None) -> tuple[str, bool]:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont, TTFError
    non_latin = any(ord(char) > 255 for text in texts for char in text)
    if not non_latin and font_path is None:
        return "Helvetica", False
    candidates = [font_path] if font_path else [
        Path("/System/Library/Fonts/STHeiti Light.ttc"),
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simsun.ttc"),
        Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansSC-Regular.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJKsc-Regular.ttf"),
    ]
    required = {ord(char) for text in texts for char in text if not char.isspace()}
    for path in candidates:
        if path is None or not path.is_file():
            continue
        try:
            name = "ResumeFont" + hashlib.sha256(str(path).encode()).hexdigest()[:12]
            font = TTFont(name, str(path))
            if not required.issubset(font.face.charToGlyph):
                continue
            pdfmetrics.registerFont(font)
            return name, True
        except (OSError, TTFError):
            continue
    raise ValueError("No embeddable TrueType font covers all approved characters. "
                     "Pass --font /path/to/a/Chinese-capable.ttf (or TrueType .ttc), "
                     "or use --format html; do not replace approved wording silently.")


def write_pdf(document: dict, target: Path, font_path: Path | None = None) -> dict:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF export requires reportlab and pypdf in this Python environment; "
                           "install them with python -m pip install reportlab pypdf, "
                           "or use --format html for a printable HTML file") from exc
    texts = _all_text(document)
    cjk = any(ord(char) > 255 for text in texts for char in text)
    font, embedded = _pdf_font(texts, font_path)
    styles = {
        "title": ParagraphStyle("Title", fontName=font, fontSize=24, leading=30, spaceAfter=10),
        "contact": ParagraphStyle("Contact", fontName=font, fontSize=10, leading=15, spaceAfter=3),
        "heading": ParagraphStyle("Heading", fontName=font, fontSize=12, leading=18,
                                  spaceBefore=14, spaceAfter=7, keepWithNext=True,
                                  textColor=colors.HexColor("#1f4e68")),
        "body": ParagraphStyle("Body", fontName=font, fontSize=10.5, leading=16,
                               spaceAfter=9, splitLongWords=True, allowWidows=0, allowOrphans=0),
    }
    if cjk:
        for style in styles.values():
            style.wordWrap = "CJK"
    story = [Paragraph(marked_text(document["title"]), styles["title"])]
    story.extend(Paragraph(marked_text(item), styles["contact"]) for item in document["contacts"])
    story.append(Spacer(1, 5))
    for section in document["sections"]:
        story.append(Paragraph(html.escape(section["heading"]), styles["heading"]))
        story.extend(Paragraph(marked_text(item), styles["body"]) for item in section["blocks"])
    pdf = SimpleDocTemplate(str(target), pagesize=A4, leftMargin=51, rightMargin=51,
                            topMargin=48, bottomMargin=48, title=document["title"], author="",
                            subject="Resume", pageCompression=1)
    pdf.build(story)
    reader = PdfReader(target)
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    normalized = re.sub(r"\s+", "", extracted)
    cursor = 0
    for text in texts:
        expected = re.sub(r"\s+", "", text)
        position = normalized.find(expected, cursor)
        if position < 0:
            raise ValueError("PDF text extraction or reading order differs from approved content; "
                             "use HTML and inspect the font/rendering before delivering")
        cursor = position + len(expected)
    return {"page_count": len(reader.pages), "text_order_verified": True,
            "visual_review_required": True,
            "font": font, "font_embedded": embedded}


def export_resume(workspace_root: Path, plan: dict, output_dir: Path, output_format: str = "both",
                  font_path: Path | None = None) -> dict:
    code, errors = validate_workspace(workspace_root)
    if code:
        raise ValueError("content handoff is not ready: " + "; ".join(errors))
    package_path = workspace_root / ".resume-site-work/input/approved-copy.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    document = document_from_plan(package, plan)
    if output_format not in {"both", "pdf", "html"}:
        raise ValueError("format must be both, pdf, or html")
    output_dir = output_dir.resolve()
    site_path = (workspace_root / ".resume-site-work/site").resolve()
    if output_dir == site_path or site_path in output_dir.parents:
        raise ValueError("export outside the site directory; copy only an approved public PDF into site/public")
    if output_dir.exists():
        raise FileExistsError("output directory already exists; use a new revision directory")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".resume-export-", dir=output_dir.parent))
    try:
        report = {"schema_version": 1, "audience": document["audience"],
                  "package_revision": document["package_revision"],
                  "package_sha256": document["package_sha256"], "block_ids": document["block_ids"],
                  "files": {}, "visual_review_required": output_format != "html"}
        if output_format in {"both", "html"}:
            write_html(document, staging / "resume.html")
        if output_format in {"both", "pdf"}:
            report["pdf_checks"] = write_pdf(document, staging / "resume.pdf", font_path)
        for path in staging.iterdir():
            report["files"][path.name] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                         "bytes": path.stat().st_size}
        (staging / "export-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                                    encoding="utf-8")
        staging.rename(output_dir)
        return report
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--plan", type=Path, help="resume-export.json selecting approved blocks")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--format", choices=("both", "pdf", "html"), default="both")
    parser.add_argument("--font", type=Path, help="embeddable TrueType font covering all resume characters")
    parser.add_argument("--package-hash", action="store_true", help="print the current package digest for a plan")
    args = parser.parse_args(argv)
    try:
        if args.package_hash:
            package = json.loads((args.workspace_root / ".resume-site-work/input/approved-copy.json")
                                 .read_text(encoding="utf-8"))
            print(package_digest(package))
            return 0
        if not args.plan or not args.output_dir:
            parser.error("--plan and --output-dir are required for export")
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        report = export_resume(args.workspace_root.resolve(), plan, args.output_dir, args.format, args.font)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, TypeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
