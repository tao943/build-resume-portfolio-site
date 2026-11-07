"""Read-only checks for the current interpreter and optional local resume tools."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _version(value: str) -> tuple[int, int, int] | None:
    match = re.search(r"(?:^|\s)v?(\d+)\.(\d+)(?:\.(\d+))?", value)
    return tuple(int(item or 0) for item in match.groups()) if match else None


def _command(name: str) -> dict:
    executable = shutil.which(name)
    if not executable:
        return {"available": False, "path": None, "version": None}
    flag = "-v" if name == "pdftoppm" else "--version"
    try:
        result = subprocess.run([executable, flag], capture_output=True, text=True,
                                timeout=10, check=False)
        value = (result.stdout or result.stderr).strip().splitlines()
        return {"available": result.returncode == 0, "path": executable,
                "version": value[0] if value else None}
    except (OSError, subprocess.TimeoutExpired):
        return {"available": False, "path": executable, "version": None}


def inspect_environment(required_features: list[str] | None = None) -> dict:
    required = set(required_features or [])
    checks = []

    def add(name: str, available: bool, needed: bool, action: str, **details: object) -> None:
        checks.append({"name": name, "available": available, "required": needed,
                       "action": None if available else action, **details})

    add("python", sys.version_info >= (3, 10), True,
        "Use Python 3.10+ and run this check again with that interpreter.",
        path=sys.executable, version=sys.version.split()[0])
    node = _command("node")
    node_version = _version(node["version"] or "")
    add("node", bool(node["available"] and node_version and node_version >= (22, 12, 0)), True,
        "Install a supported Node.js LTS release (22.12+) with npm; reopen the terminal so both are on PATH.",
        path=node["path"], version=node["version"])
    npm = _command("npm")
    add("npm", npm["available"], True,
        "Install npm with Node.js, then check that npm --version works in this terminal.",
        path=npm["path"], version=npm["version"])
    for package, feature in [("pdfplumber", "pdf-import"), ("reportlab", "pdf-export"), ("pypdf", "pdf-export")]:
        try:
            available = importlib.util.find_spec(package) is not None
        except (ImportError, ValueError):
            available = False
        add(package, available, feature in required,
            f"Install {package} into a local virtual environment and rerun with its Python; see references/import-guide.md.")
    for command, feature in [("pdftoppm", "pdf-audit"), ("tesseract", "ocr")]:
        details = _command(command)
        add(command, details["available"], feature in required,
            "Install Poppler locally for PDF rendering / scanned-PDF OCR." if command == "pdftoppm" else
            "Install Tesseract locally with the needed language data; OCR only runs when explicitly requested.",
            path=details["path"], version=details["version"])
    availability = {item["name"]: item["available"] for item in checks}
    languages = []
    if availability["tesseract"]:
        try:
            result = subprocess.run([shutil.which("tesseract"), "--list-langs"],
                                    capture_output=True, text=True, timeout=10, check=False)
            if result.returncode == 0:
                languages = [line.strip() for line in result.stdout.splitlines()
                             if re.fullmatch(r"[A-Za-z0-9_]+", line.strip())]
        except (OSError, subprocess.TimeoutExpired):
            pass
    return {
        "schema_version": 1,
        "status": "blocked" if any(item["required"] and not item["available"] for item in checks) else "ready",
        "checks": checks,
        "capabilities": {
            "docx_text_import": True,
            "pdf_import": availability["pdfplumber"],
            "pdf_export": availability["reportlab"] and availability["pypdf"],
            "pdf_visual_audit": availability["pdftoppm"],
            "image_ocr": availability["tesseract"],
            "scanned_pdf_ocr": availability["tesseract"] and availability["pdftoppm"] and availability["pdfplumber"],
        },
        "ocr_languages": languages,
        "notes": ["No packages were installed and no documents were uploaded.",
                  "Available tools still need a real document/build check; this report does not certify output quality.",
                  "Non-Latin PDF export also needs a local embeddable font covering the text; export_resume.py verifies glyphs and accepts --font.",
                  "Optional gaps do not block ordinary DOCX/text preparation. Request only the features you need."],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require", action="append", choices=["pdf-import", "pdf-export", "pdf-audit", "ocr"], default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = inspect_environment(args.require)
    value = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(value + "\n", encoding="utf-8")
    else:
        print(value)
    return 0 if report["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
