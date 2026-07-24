from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence

from validate_design_catalog import validate_catalog as validate_design_catalog
from validate_motion_catalog import validate_catalog as validate_motion_catalog


PROMPT_SPECS = {
    "generate-prototype": ("01-generate-prototype.md", "react-vite-project"),
    "analyze-reference": ("02-analyze-reference.md", "style-brief-json"),
    "direct-media-art": (
        "03-direct-media-art.md",
        "react-vite-project-update-and-media-art-direction-json",
    ),
    "audit-screenshot": ("04-audit-screenshot.md", "visual-audit-json"),
    "repair-local-issues": ("05-repair-local-issues.md", "react-vite-project-update"),
    "add-motion": ("06-add-motion.md", "react-vite-project-update-and-motion-plan-json"),
    "select-motion-enhancement": ("07-select-motion-enhancement.md", "motion-enhancement-selection-json"),
    "plan-motion-media": ("08-plan-motion-media.md", "motion-media-slot-json-and-poster"),
    "apply-motion-enhancement": (
        "09-apply-motion-enhancement.md",
        "react-vite-project-update-and-motion-enhancement-plan-json",
    ),
    "upgrade-poster-to-video": (
        "10-upgrade-poster-to-video.md",
        "react-vite-media-only-update-and-video-validation-json",
    ),
}

STAGE_RESOURCES = {
    "prototype": ("generate-prototype", "design-catalog"),
    "media-direction": (
        "analyze-reference",
        "direct-media-art",
        "reference-library",
        "design-catalog",
    ),
    "screenshot": ("audit-screenshot", "repair-local-issues"),
    "motion": ("add-motion",),
    "motion-enhancement": (
        "select-motion-enhancement", "plan-motion-media",
        "apply-motion-enhancement", "motion-catalog",
    ),
    "video-upgrade": ("upgrade-poster-to-video", "motion-catalog"),
}

ALLOWED_STATUSES = {"awaiting-user-supplied-content", "ready"}
REFERENCE_FIELDS = {
    "id",
    "path",
    "role_tags",
    "visual_tags",
    "source_note",
    "license_note",
    "aspect_ratio",
    "available",
}


@dataclass(frozen=True)
class ResourceReport:
    ok: bool
    mode: str
    stage: str | None
    ready: bool
    errors: tuple[str, ...]


def parse_prompt_header(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening frontmatter delimiter")
    try:
        closing_index = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration as error:
        raise ValueError("missing closing frontmatter delimiter") from error

    metadata: dict[str, object] = {}
    for line in lines[1:closing_index]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key or not value:
            raise ValueError(f"invalid frontmatter line: {line}")
        metadata[key] = int(value) if value.isdigit() else value
    metadata["body"] = "\n".join(lines[closing_index + 1 :]).strip()
    return metadata


def _validate_prompt(root: Path, resource_id: str, require_ready: bool) -> tuple[list[str], bool]:
    filename, output_contract = PROMPT_SPECS[resource_id]
    path = root / "prompts" / filename
    if not path.is_file():
        return [f"missing_prompt: {resource_id}"], False
    try:
        metadata = parse_prompt_header(path)
    except (OSError, UnicodeError, ValueError) as error:
        return [f"invalid_prompt: {resource_id}: {error}"], False

    structural_errors: list[str] = []
    if metadata.get("resource_id") != resource_id:
        structural_errors.append(f"invalid_prompt_id: {resource_id}")
    if metadata.get("output_contract") != output_contract:
        structural_errors.append(f"invalid_output_contract: {resource_id}")
    status = metadata.get("resource_status")
    if status not in ALLOWED_STATUSES:
        structural_errors.append(f"invalid_resource_status: {resource_id}")
    version = metadata.get("resource_version")
    if not isinstance(version, int) or version < 0:
        structural_errors.append(f"invalid_resource_version: {resource_id}")
    body = metadata.get("body")
    if not isinstance(body, str) or not body:
        structural_errors.append(f"empty_prompt_body: {resource_id}")
    if structural_errors:
        return structural_errors, False

    ready = status == "ready" and isinstance(version, int) and version >= 1
    if ready and "intentionally unavailable" in str(body).lower():
        return [f"invalid_ready_prompt_body: {resource_id}"], False
    if require_ready and not ready:
        return [f"resource_not_ready: {resource_id}"], False
    return [], ready


def validate_reference_manifest(path: Path, require_ready: bool) -> tuple[list[str], bool]:
    if not path.is_file():
        return ["missing_reference_manifest"], False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return [f"invalid_reference_manifest: {error}"], False

    structural_errors: list[str] = []
    if data.get("schema_version") != 1:
        structural_errors.append("invalid_reference_schema_version")
    status = data.get("library_status")
    if status not in ALLOWED_STATUSES:
        structural_errors.append("invalid_reference_library_status")
    version = data.get("library_version")
    if not isinstance(version, int) or version < 0:
        structural_errors.append("invalid_reference_library_version")
    references = data.get("references")
    if not isinstance(references, list):
        structural_errors.append("invalid_reference_items")
        references = []

    ready = status == "ready" and isinstance(version, int) and version >= 1 and bool(references)
    if status == "ready":
        if not ready:
            structural_errors.append("invalid_ready_reference_library")
        for index, item in enumerate(references):
            if not isinstance(item, dict) or not REFERENCE_FIELDS.issubset(item):
                structural_errors.append(f"invalid_reference_item: {index}")
                continue
            relative_path = str(item["path"]).replace("\\", "/")
            pure_path = PurePosixPath(relative_path)
            if pure_path.is_absolute() or ".." in pure_path.parts:
                structural_errors.append(f"invalid_reference_path: {relative_path}")
                continue
            if item.get("available") is True and not (path.parent / Path(relative_path)).is_file():
                structural_errors.append(f"missing_reference_asset: {relative_path}")

    if structural_errors:
        return structural_errors, False
    if require_ready and not ready:
        return ["resource_not_ready: reference-library"], False
    return [], ready


def validate_resources(skill_root: Path, mode: str, stage: str | None, workspace_root: Path | None = None) -> ResourceReport:
    if mode not in {"skeleton", "runtime"}:
        return ResourceReport(False, mode, stage, False, (f"invalid_mode: {mode}",))
    if mode == "runtime" and stage not in STAGE_RESOURCES:
        return ResourceReport(False, mode, stage, False, (f"invalid_stage: {stage}",))

    workspace_root = workspace_root.resolve() if workspace_root is not None else None
    resources = (
        tuple(PROMPT_SPECS) + ("reference-library", "motion-catalog", "design-catalog")
        if mode == "skeleton"
        else STAGE_RESOURCES[stage]
    )
    errors: list[str] = []
    readiness: list[bool] = []
    require_ready = mode == "runtime"
    for resource_id in resources:
        if resource_id == "reference-library":
            workspace_manifest = (
                workspace_root / ".resume-site-work" / "reference-library" / "manifest.json"
                if workspace_root is not None and mode == "runtime" and stage == "media-direction"
                else skill_root / "assets" / "reference-library" / "manifest.json"
            )
            if mode == "runtime" and stage == "media-direction":
                if workspace_manifest.is_file():
                    resource_errors, _ = validate_reference_manifest(
                        workspace_manifest,
                        require_ready=False,
                    )
                    resource_ready = not resource_errors
                else:
                    resource_errors, resource_ready = [], True
            else:
                resource_errors, resource_ready = validate_reference_manifest(
                    workspace_manifest,
                    require_ready,
                )
        elif resource_id == "design-catalog":
            design_report = validate_design_catalog(
                skill_root / "vendor" / "ui-ux-pro-max"
            )
            resource_errors = [
                f"invalid_design_catalog: {error}" for error in design_report.errors
            ]
            resource_ready = design_report.ok
        elif resource_id == "motion-catalog":
            catalog_report = validate_motion_catalog(
                skill_root / "assets" / "motion-enhancement" / "catalog",
                require_ready=require_ready,
            )
            resource_errors = []
            for error in catalog_report.errors:
                if error.startswith("resource_not_ready"):
                    resource_errors.append("resource_not_ready: motion-catalog")
                else:
                    resource_errors.append(f"invalid_motion_catalog: {error}")
            resource_ready = catalog_report.ready
        else:
            resource_errors, resource_ready = _validate_prompt(
                skill_root, resource_id, require_ready
            )
        errors.extend(resource_errors)
        readiness.append(resource_ready)

    structural_prefixes = (
        "missing_",
        "invalid_",
        "empty_",
    )
    ok = not any(error.startswith(structural_prefixes) for error in errors)
    ready = ok and bool(readiness) and all(readiness)
    return ResourceReport(ok, mode, stage, ready, tuple(errors))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate staged skill resources.")
    parser.add_argument("--mode", choices=("skeleton", "runtime"), required=True)
    parser.add_argument("--stage", choices=tuple(STAGE_RESOURCES))
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--workspace-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    report = validate_resources(args.skill_root, args.mode, args.stage, args.workspace_root)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    if not report.ok:
        return 1
    if not report.ready and args.mode == "runtime":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
