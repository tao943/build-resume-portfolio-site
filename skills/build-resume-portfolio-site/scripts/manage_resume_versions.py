"""Save, compare and select approved resume versions without replacing the factual master."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

from validate_content_handoff import validate_workspace

FILES = (
    "input/source-manifest.json", "input/normalized-resume.json", "input/approved-copy.json",
    "reports/content-provenance.json", "reports/content-quality-review.json",
)
NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def facts_by_id(package: dict) -> dict:
    result = {}
    def visit(value):
        if isinstance(value, dict):
            if "fact_id" in value:
                fact_id = value["fact_id"]
                if not isinstance(fact_id, str) or fact_id in result:
                    raise ValueError("Fact IDs must be unique strings")
                result[fact_id] = value
            else:
                for child in value.values():
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(package["source_facts"])
    return result


def validate_references(package: dict, quality: dict, jd: dict | None) -> None:
    facts = facts_by_id(package)
    evidence = {row["evidence_id"]: row for row in package["evidence"]}
    if len(evidence) != len(package["evidence"]):
        raise ValueError("Evidence IDs must be unique")
    for block in package["approved_copy"].values():
        if not isinstance(block.get("text"), str) or not block["text"].strip():
            raise ValueError("Approved copy must have non-empty text")
        if not set(block["fact_ids"]) <= set(facts):
            raise ValueError("Approved copy references unknown fact IDs")
    references = list(quality["blocks"]) + ((jd or {}).get("matches", []))
    for block in quality["blocks"]:
        if block.get("stronger_version") is not None:
            references.append(block["stronger_version"])
        if block.get("result") is not None:
            references.append(block["result"])
    for row in references:
        if not set(row["fact_ids"]) <= set(facts) or not set(row["evidence_ids"]) <= set(evidence):
            raise ValueError("Review or JD references unknown facts/evidence")
    # Matching remains an Agent-reviewed semantic judgment; IDs alone cannot prove a claim.


def library(root: Path) -> Path:
    return root.resolve() / ".resume-site-work" / "content-versions"


def version_path(root: Path, name: str) -> Path:
    if not NAME.fullmatch(name):
        raise ValueError("Use a version name of 1-64 lowercase letters, digits or hyphens")
    path = library(root) / name
    if path.is_symlink():
        raise ValueError("Version directories may not be symlinks")
    return path


def checked_content(root: Path) -> tuple[dict, dict, dict | None]:
    status, messages = validate_workspace(root)
    if status:
        raise ValueError("CONTENT_READY required: " + "; ".join(messages))
    work = root / ".resume-site-work"
    package = read_json(work / "input/approved-copy.json")
    quality = read_json(work / "reports/content-quality-review.json")
    jd = read_json(work / "reports/jd-match.json") if quality["jd_review"]["present"] else None
    validate_references(package, quality, jd)
    return package, quality, jd


def master_hash(package: dict) -> str:
    return digest({key: package[key] for key in ("source_facts", "evidence")})


def load_version(root: Path, name: str) -> tuple[dict, dict, dict, dict | None]:
    destination = version_path(root, name)
    metadata = read_json(destination / "version.json")
    if metadata.get("name") != name or metadata.get("schema_version") != 1:
        raise ValueError("Invalid version metadata")
    for relative, expected in metadata["files"].items():
        if relative not in FILES + ("reports/jd-match.json",):
            raise ValueError("Invalid version file entry")
        path = destination / ".resume-site-work" / relative
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Saved content changed; save approved changes as a new version")
    package, quality, jd = checked_content(destination)
    if master_hash(package) != metadata["master_hash"] or digest(package) != metadata["package_hash"]:
        raise ValueError("Version integrity mismatch")
    return metadata, package, quality, jd


def save_version(root: Path, source: Path, name: str, label: str | None = None) -> dict:
    destination = version_path(root, name)
    if destination.exists():
        raise FileExistsError("Version already exists; use a new name such as frontend-v2")
    package, _, jd = checked_content(source)
    factual_hash = master_hash(package)
    if name != "general":
        general, _, _, _ = load_version(root, "general")
        if factual_hash != general["master_hash"]:
            raise ValueError("Role versions must preserve the general version's facts and evidence")
        if jd is None:
            raise ValueError("A role version requires its validated JD match report")
    elif jd is not None:
        raise ValueError("Save a general version without a JD before creating role versions")
    library(root).mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".version-", dir=library(root)))
    try:
        checksums = {}
        for relative in FILES + (("reports/jd-match.json",) if jd else ()):
            original = source / ".resume-site-work" / relative
            if original.is_symlink():
                raise ValueError("Handoff files may not be symlinks")
            target = temporary / ".resume-site-work" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = original.read_bytes()
            target.write_bytes(raw)
            checksums[relative] = hashlib.sha256(raw).hexdigest()
        checked_content(temporary)
        metadata = {"schema_version": 1, "name": name, "label": label or name,
                    "target_role": jd["target_role"] if jd else "", "organization": jd["organization"] if jd else "",
                    "revision": package["handoff"]["revision"], "master_hash": factual_hash,
                    "package_hash": digest(package), "files": checksums}
        (temporary / "version.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.rename(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return {**metadata, "workspace": str(destination)}


def list_versions(root: Path) -> list[dict]:
    if not library(root).exists():
        return []
    rows = []
    for path in sorted(library(root).iterdir()):
        if not path.name.startswith(".") and path.is_dir():
            metadata, _, _, _ = load_version(root, path.name)
            rows.append({key: metadata[key] for key in ("name", "label", "target_role", "organization", "revision")})
    return rows


def compare_versions(root: Path, before: str, after: str) -> dict:
    _, old, old_quality, _ = load_version(root, before)
    metadata, new, quality, jd = load_version(root, after)
    if master_hash(old) != master_hash(new):
        raise ValueError("Cannot compare versions from different factual masters")
    facts = facts_by_id(new)
    evidence = {row["evidence_id"]: row for row in new["evidence"]}
    review = {row["block_id"]: row for row in quality["blocks"]}
    old_review = {row["block_id"]: row for row in old_quality["blocks"]}
    changes = []
    old_copy, new_copy = old["approved_copy"], new["approved_copy"]
    for block_id in sorted(set(old_copy) | set(new_copy)):
        a, b = old_copy.get(block_id), new_copy.get(block_id)
        if a == b or (a and b and a["text"] == b["text"] and a["fact_ids"] == b["fact_ids"]):
            continue
        fact_ids = b["fact_ids"] if b else a["fact_ids"]
        selected_review = review[block_id] if b else old_review[block_id]
        selected_copy = (selected_review["stronger_version"]
                         if selected_review["selected_version"] == "stronger" else selected_review)
        evidence_ids = selected_copy["evidence_ids"]
        changes.append({"block_id": block_id, "change": "added" if a is None else "removed" if b is None else "changed",
                        "before": a["text"] if a else None, "after": b["text"] if b else None,
                        "facts": [facts[key] for key in fact_ids], "evidence": [evidence[key] for key in evidence_ids]})
    requirements = {row["id"]: row for row in (jd or {}).get("requirements", [])}
    gaps = [{**requirements[row["jd_item_id"]], "status": row["status"], "rationale": row["rationale"]}
            for row in (jd or {}).get("matches", []) if row["status"] != "strong_match"]
    return {"schema_version": 1, "before": before, "after": after,
            "target_role": metadata["target_role"], "changes": changes,
            "before_order": list(old_copy), "after_order": list(new_copy), "gaps": gaps,
            "clarification_candidates": (jd or {}).get("clarification_candidates", [])}


def compare_markdown(report: dict) -> str:
    def safe(value):
        return str(value).replace("<", "&lt;").replace(">", "&gt;").replace("[", "\\[").replace("`", "\\`")
    lines = [f"# {safe(report['before'])} → {safe(report['after'])}", "", "本报告仅供本地审阅，包含事实与证据，不应发布到作品集。", ""]
    for row in report["changes"]:
        lines += [f"## {safe(row['block_id'])}", f"- 原文：{safe(row['before'] or '（无）')}",
                  f"- 新文：{safe(row['after'] or '（移除）')}"]
        for fact in row["facts"]:
            lines.append(f"- 事实 {safe(fact['fact_id'])}：{safe(fact['value'])}")
        for evidence in row["evidence"]:
            lines.append(f"- 证据 {safe(evidence['evidence_id'])}：{safe(evidence['quote'])}（{safe(evidence['location'])}）")
        lines.append("")
    if report["before_order"] != report["after_order"]:
        lines += ["## 顺序变化", safe(" → ".join(report["before_order"])), safe(" → ".join(report["after_order"])), ""]
    lines += ["## 待补充与部分匹配"]
    lines += [f"- {safe(row['exact_phrase'])} [{safe(row['status'])}]：{safe(row['rationale'])}" for row in report["gaps"]] or ["- 没有记录的缺口；不代表已验证录用条件。"]
    lines += [f"- 待核实：{safe(text)}" for text in report["clarification_candidates"]]
    return "\n".join(lines) + "\n"


def select_version(root: Path, name: str) -> dict:
    metadata, _, _, _ = load_version(root, name)
    result = {"schema_version": 1, "name": name, "package_hash": metadata["package_hash"],
              "workspace": str(version_path(root, name)),
              "next_action": "Use this workspace for PDF export or site generation. Save changed copy as a new version."}
    path = library(root) / "active-version.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    save = commands.add_parser("save")
    save.add_argument("name")
    save.add_argument("--source-workspace", type=Path)
    save.add_argument("--label")
    commands.add_parser("list")
    compare = commands.add_parser("compare")
    compare.add_argument("before")
    compare.add_argument("after")
    compare.add_argument("--output", type=Path, help="New local .md or .json report; never published")
    select = commands.add_parser("select")
    select.add_argument("name")
    args = parser.parse_args()
    try:
        if args.command == "save":
            result = save_version(args.workspace_root, args.source_workspace or args.workspace_root, args.name, args.label)
        elif args.command == "list":
            result = list_versions(args.workspace_root)
        elif args.command == "select":
            result = select_version(args.workspace_root, args.name)
        else:
            result = compare_versions(args.workspace_root, args.before, args.after)
            if args.output:
                content = compare_markdown(result) if args.output.suffix == ".md" else json.dumps(result, ensure_ascii=False, indent=2)
                with args.output.open("x", encoding="utf-8") as stream:
                    stream.write(content)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
