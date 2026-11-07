"""Write an approved content package into the portfolio builder input boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from validate_content_package import validate
from validate_content_handoff import validate_workspace


HANDOFF_FILES = (
    "input/source-manifest.json", "input/normalized-resume.json", "input/approved-copy.json",
    "reports/content-provenance.json", "reports/content-quality-review.json", "reports/jd-match.json",
)


def _require_valid(root: Path, label: str) -> None:
    status, messages = validate_workspace(root)
    if status:
        raise ValueError(label + ": " + "; ".join(messages))


def write_input(package_path: Path, workspace_root: Path, revision: int | None = None, *,
                quality_review_path: Path | None = None, jd_report_path: Path | None = None) -> list[Path]:
    workspace_root = workspace_root.resolve()
    package = json.loads(package_path.read_text(encoding="utf-8"))
    errors = validate(package)
    if errors:
        raise ValueError("; ".join(errors))
    if package.get("handoff", {}).get("status") != "approved":
        raise ValueError("Obtain content approval before writing the handoff")
    next_revision = revision if revision is not None else package["handoff"].get("revision", 1)
    if type(next_revision) is not int or next_revision < 1:
        raise ValueError("revision must be a positive integer")
    work = workspace_root / ".resume-site-work"
    destination = work / "input"
    existing = destination / "approved-copy.json"
    snapshot = None
    if existing.exists():
        _require_valid(workspace_root, "Existing handoff is invalid; restore its reports and stage new reports elsewhere before updating")
        current = json.loads(existing.read_text(encoding="utf-8"))
        if current.get("handoff", {}).get("status") == "approved" and revision is None:
            raise FileExistsError("approved-copy.json exists; pass --revision to create a new revision")
        if next_revision <= current.get("handoff", {}).get("revision", 0):
            raise ValueError("revision must increase; previous content must remain recoverable")
        snapshot = destination.parent / "versions" / f"content-r{current['handoff']['revision']}"
        if snapshot.exists():
            raise FileExistsError(f"Snapshot already exists: {snapshot}")
    quality_path = quality_review_path or work / "reports/content-quality-review.json"
    if not quality_path.is_file():
        raise ValueError("Provide the approved quality report with --quality-review; stage it outside the current handoff")
    quality = json.loads(quality_path.read_text(encoding="utf-8"))
    package["handoff"]["revision"] = next_revision
    package["handoff"]["status"] = "approved"
    files = {
        "input/source-manifest.json": {"schema_version": 1, "source_hashes": package["handoff"].get("source_hashes", [])},
        "input/normalized-resume.json": {"schema_version": 1, "source_facts": package["source_facts"], "evidence": package["evidence"]},
        "input/approved-copy.json": package,
        "reports/content-quality-review.json": quality,
        "reports/content-provenance.json": {
            "schema_version": 1,
            "package_revision": next_revision,
            "package_hash": hashlib.sha256(json.dumps(package, ensure_ascii=False, indent=2).encode("utf-8")).hexdigest(),
            "evidence_count": len(package["evidence"]),
        },
    }
    if quality.get("jd_review", {}).get("present") is True:
        jd_path = jd_report_path or work / "reports/jd-match.json"
        if not jd_path.is_file():
            raise ValueError("The quality report requires a JD report; provide it with --jd-report")
        files["reports/jd-match.json"] = json.loads(jd_path.read_text(encoding="utf-8"))
    elif jd_report_path is not None:
        raise ValueError("--jd-report was supplied but the quality report declares no JD")
    workspace_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".handoff-", dir=workspace_root) as temporary:
        staging_root = Path(temporary)
        staged_work = staging_root / ".resume-site-work"
        for relative, content in files.items():
            target = staged_work / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
        _require_valid(staging_root, "New staged handoff is invalid; current files were not changed")
        previous = {relative: (work / relative).read_bytes() if (work / relative).is_file() else None
                    for relative in HANDOFF_FILES}
        if snapshot is not None:
            staged_snapshot = staging_root / "snapshot"
            for relative, raw in previous.items():
                if raw is not None:
                    target = staged_snapshot / ".resume-site-work" / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(raw)
            _require_valid(staged_snapshot, "Old handoff snapshot failed validation")
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            staged_snapshot.rename(snapshot)
        try:
            for relative in HANDOFF_FILES:
                target = work / relative
                if relative in files:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    (staged_work / relative).replace(target)
                elif target.exists():
                    target.unlink()
            _require_valid(workspace_root, "Written handoff failed validation")
        except Exception:
            # Keep a complete recoverable snapshot if restoration itself fails.
            for relative, raw in previous.items():
                target = work / relative
                if raw is None:
                    if target.exists():
                        target.unlink()
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(raw)
            if snapshot is not None:
                shutil.rmtree(snapshot)
            raise
    return [work / relative for relative in files]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument("--revision", type=int)
    parser.add_argument("--quality-review", type=Path, help="Approved quality report staged outside the current handoff")
    parser.add_argument("--jd-report", type=Path, help="Staged JD match report when the quality review includes a JD")
    args = parser.parse_args()
    try:
        for path in write_input(args.package, args.workspace_root, args.revision,
                                quality_review_path=args.quality_review, jd_report_path=args.jd_report):
            print(path)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
