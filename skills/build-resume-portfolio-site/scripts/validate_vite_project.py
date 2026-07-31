from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


STAGES = ("prototype", "styled", "media-direction", "refined", "integrated", "motion", "motion-enhanced", "video-upgrade")
MOTION_STAGES = {"media-direction", "integrated", "motion", "motion-enhanced", "video-upgrade"}
SOURCE_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".css", ".scss", ".sass"}
SKIPPED_DIRS = {"node_modules", "dist", ".git", ".resume-site-work"}
REGION_PATTERNS = {
    "hero": (r"(?:id|data-section)\s*=\s*[\"']hero[\"']", r"\bHero\b"),
    "experience": (
        r"(?:id|data-section)\s*=\s*[\"'](?:experience|about)[\"']",
        r"\b(?:Experience|About)\b",
        r"个人经历|个人介绍|关于我",
    ),
    "projects": (
        r"(?:id|data-section)\s*=\s*[\"'](?:projects|portfolio)[\"']",
        r"\b(?:Projects|Portfolio)\b",
        r"精选项目|项目经历|作品",
    ),
    "strengths": (
        r"(?:id|data-section)\s*=\s*[\"'](?:strengths|advantages)[\"']",
        r"\b(?:Strengths|Advantages)\b",
        r"个人优势|核心能力",
    ),
    "contact": (
        r"(?:id|data-section)\s*=\s*[\"']contact[\"']",
        r"\bContact\b",
        r"联系方式|联系我",
    ),
}


@dataclass(frozen=True)
class ViteProjectReport:
    ok: bool
    stage: str
    project_dir: str
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _add_once(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _load_package(path: Path, errors: list[str]) -> dict[str, object]:
    if not path.is_file():
        errors.append("missing_package_json")
        return {}
    try:
        data = json.loads(_read_text(path))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors.append(f"invalid_package_json: {error}")
        return {}
    if not isinstance(data, dict):
        errors.append("invalid_package_json: root_must_be_object")
        return {}
    return data


def _source_files(project_dir: Path) -> list[Path]:
    source_root = project_dir / "src"
    if not source_root.is_dir():
        return []
    files: list[Path] = []
    for path in source_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        if any(part in SKIPPED_DIRS for part in path.relative_to(project_dir).parts):
            continue
        files.append(path)
    return sorted(files)


def validate_vite_project(project_dir: Path, stage: str) -> ViteProjectReport:
    project_dir = project_dir.resolve()
    if stage not in STAGES:
        return ViteProjectReport(False, stage, str(project_dir), (f"invalid_stage: {stage}",), ())

    errors: list[str] = []
    warnings: list[str] = []
    if not project_dir.is_dir():
        return ViteProjectReport(False, stage, str(project_dir), ("project_directory_not_found",), ())

    package = _load_package(project_dir / "package.json", errors)
    scripts = package.get("scripts", {}) if isinstance(package, dict) else {}
    if not isinstance(scripts, dict):
        scripts = {}
    dev_script = scripts.get("dev")
    build_script = scripts.get("build")
    if not isinstance(dev_script, str) or "vite" not in dev_script.lower():
        errors.append("missing_dev_script")
    if (
        not isinstance(build_script, str)
        or "vite" not in build_script.lower()
        or "build" not in build_script.lower()
    ):
        errors.append("missing_build_script")

    dependencies: dict[str, object] = {}
    for key in ("dependencies", "devDependencies"):
        values = package.get(key, {}) if isinstance(package, dict) else {}
        if isinstance(values, dict):
            dependencies.update(values)
    for dependency in ("react", "react-dom", "vite"):
        if dependency not in dependencies:
            errors.append(f"missing_dependency: {dependency}")

    index_path = project_dir / "index.html"
    try:
        index_html = _read_text(index_path)
    except (OSError, UnicodeError) as error:
        errors.append(f"index_html_read_error: {error}")
        index_html = ""

    if not re.search(r"<[^>]+id\s*=\s*[\"']root[\"']", index_html, re.IGNORECASE):
        errors.append("missing_root_mount")
    entry_match = re.search(
        r"<script\b[^>]*\btype\s*=\s*[\"']module[\"'][^>]*\bsrc\s*=\s*[\"']([^\"']+)[\"']",
        index_html,
        re.IGNORECASE,
    ) or re.search(
        r"<script\b[^>]*\bsrc\s*=\s*[\"']([^\"']+)[\"'][^>]*\btype\s*=\s*[\"']module[\"']",
        index_html,
        re.IGNORECASE,
    )
    if not entry_match:
        errors.append("missing_module_entry")
    else:
        entry_value = entry_match.group(1).split("?", 1)[0].lstrip("/")
        if not (project_dir / entry_value).is_file():
            errors.append(f"missing_entry_file: {entry_value}")

    source_files = _source_files(project_dir)
    if not source_files:
        errors.append("missing_source_files")
    source_parts: list[str] = []
    for path in source_files:
        try:
            source_parts.append(_read_text(path))
        except (OSError, UnicodeError) as error:
            errors.append(f"source_read_error: {path.relative_to(project_dir).as_posix()}: {error}")
    source_text = "\n".join(source_parts)
    searchable = f"{index_html}\n{source_text}"

    for region, patterns in REGION_PATTERNS.items():
        if not any(re.search(pattern, searchable, re.IGNORECASE) for pattern in patterns):
            errors.append(f"missing_page_region: {region}")

    lowered = searchable.lower()
    if "javascript:" in lowered:
        errors.append("unsafe_url_scheme: javascript")
    if "data:text/html" in lowered:
        errors.append("unsafe_url_scheme: data:text/html")

    quality_findings: list[str] = []
    if not re.search(r":focus(?:-visible)?\b", source_text, re.IGNORECASE):
        quality_findings.append("missing_visible_focus_style")
    if not re.search(r"(?:max-width|--[\w-]*max[\w-]*)\s*:\s*(?:1[56-8]\d{2}|1700)px", source_text, re.IGNORECASE):
        quality_findings.append("missing_approximately_1700px_content_width")
    if stage == "prototype":
        warnings.extend(quality_findings)
    else:
        errors.extend(quality_findings)

    if stage in MOTION_STAGES and not re.search(
        r"@media\s*\(\s*prefers-reduced-motion\s*:\s*reduce\s*\)",
        source_text,
        re.IGNORECASE,
    ):
        _add_once(errors, "missing_reduced_motion_rule")

    if stage in {"motion-enhanced", "video-upgrade"}:
        if "data-motion-media" not in source_text:
            _add_once(errors, "missing_motion_media")
        poster_reference = re.search(
            r"(?:poster|src)\s*=\s*(?:\{[^}]*poster[^}]*\}|[\"'](?!https?://)[^\"']+\.(?:png|jpe?g|webp|avif)[\"'])",
            source_text,
            re.IGNORECASE,
        )
        if "<img" not in source_text.lower() or not poster_reference:
            _add_once(errors, "missing_motion_poster")

    if stage == "video-upgrade":
        video_match = re.search(r"<video\b([^>]*)>", source_text, re.IGNORECASE | re.DOTALL)
        required_attributes = ("autoplay", "muted", "loop", "playsinline", "poster", "preload")
        if not video_match:
            _add_once(errors, "invalid_video_embed_contract")
        else:
            attributes = video_match.group(1).lower()
            if (
                not all(attribute in attributes for attribute in required_attributes)
                or "metadata" not in attributes
                or "onerror" not in attributes
                or not re.search(r"[\"'](?!https?://)[^\"']+\.(?:mp4|webm)[\"']", source_text, re.IGNORECASE)
            ):
                _add_once(errors, "invalid_video_embed_contract")
        if re.search(r"https?://[^\"'\s]+\.(?:mp4|webm)", source_text, re.IGNORECASE):
            _add_once(errors, "remote_video_forbidden")
        interactive_patterns = (
            r"\b(?:video|\w*video\w*)\.currentTime\s*=",
            r"useScroll[\s\S]{0,240}(?:video|currentTime)",
            r"onPointerMove[\s\S]{0,240}(?:video|currentTime|mask|opacity)",
            r"(?:pointer[XY]|client[XY])[\s\S]{0,160}(?:video|currentTime|mask|opacity)",
        )
        if any(re.search(pattern, source_text, re.IGNORECASE) for pattern in interactive_patterns):
            _add_once(errors, "interactive_video_forbidden")

    return ViteProjectReport(not errors, stage, str(project_dir), tuple(errors), tuple(warnings))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a generated React + Vite portfolio project.")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--stage", choices=STAGES, required=True)
    args = parser.parse_args(argv)
    report = validate_vite_project(args.project_dir, args.stage)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
