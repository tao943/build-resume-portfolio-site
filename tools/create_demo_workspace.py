"""Create explicitly fictional, pre-approved QA fixtures; never use these approvals for real users."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills/build-resume-portfolio-site"
sys.path.insert(0, str(SKILL / "scripts"))
from write_resume_site_input import write_input
from validate_content_quality_review import ATS_CHECKS, INTEGRITY_CHECKS

PROFILES = {
    "experienced": {
        "name": "林遥（虚构演示）",
        "contact": "linyao@example.com",
        "summary": "前端工程师，关注 React 组件与可访问性。以下经历均为功能演示用虚构材料。",
        "work": "2022–2025，在虚构的青杉工作室参与内部工具开发，负责 React 页面与组件维护。",
        "project": "为演示订单工具实现表格筛选、键盘导航和错误提示，并编写使用说明；没有可核验的业务增长指标。",
        "education": "2018–2022，虚构示例大学，计算机科学本科。",
        "skills": "React、JavaScript、CSS、键盘可访问性检查。",
    },
    "graduate": {
        "name": "周宁（虚构演示）",
        "contact": "zhouning@example.com",
        "summary": "应届毕业生，求职方向为前端开发。以下学习和课程项目均为功能演示用虚构材料。",
        "project": "在课程阅读记录项目中负责 HTML/CSS 页面、JavaScript 本地筛选及移动端布局，并记录同学反馈；未宣称真实用户规模。",
        "education": "2022–2026，虚构示例学院，软件工程本科。",
        "skills": "HTML、CSS、JavaScript，正在学习 React。",
    },
}


def fixture(profile="experienced", role=False):
    blocks = PROFILES[profile]
    source = "source-fictional-demo"
    facts = {"basics": {}, "work": [], "education": [], "projects": [], "skills": [], "links": []}
    copy, evidence, reviews = {}, [], []
    for key, text in blocks.items():
        fid, eid = f"fact-{key}", f"evidence-{key}"
        fact = {"fact_id": fid, "value": text, "source_ids": [source], "confidence": "high", "confirmation_status": "user_confirmed"}
        section = {"work": "work", "project": "projects", "education": "education", "skills": "skills"}.get(key, "basics")
        if section == "basics":
            facts[section][key] = fact
        elif section == "skills":
            facts[section].append(fact)
        else:
            facts[section].append({"description": fact})
        evidence.append({"evidence_id": eid, "source_id": source, "quote": text, "location": f"fictional-{profile}.txt / {key}"})
        final = text
        if role and key == "summary":
            final = "关注 React 组件与可访问性的前端工程师。以下经历均为功能演示用虚构材料。"
        copy[key] = {"text": final, "fact_ids": [fid], "version": 2 if role else 1, "approval_status": "user_approved"}
        reviews.append({"block_id": key, "source_section": section, "original_copy": text,
                        "recommended_copy": final, "stronger_version": None, "selected_version": "recommended",
                        "action": "Preserve supplied fictional statement", "method": "Compare with the synthetic source",
                        "scope": "QA fixture only; not a real credential", "result": {"kind": "qualitative_fallback", "text": "No unsupported outcome added", "fact_ids": [], "evidence_ids": [], "reason": "No verified outcome metric supplied", "unsupported_metrics_removed": True},
                        "fact_ids": [fid], "evidence_ids": [eid], "jd_requirement_ids": ["react"] if role and key in ("summary", "work", "skills") else [],
                        "integrity_review": {name: True for name in INTEGRITY_CHECKS}, "approval_status": "user_approved"})
    package = {"schema_version": 1, "source_facts": facts, "evidence": evidence, "open_questions": [],
               "approved_copy": copy, "handoff": {"status": "approved", "revision": 2 if role else 1,
               "source_hashes": [hashlib.sha256(json.dumps(blocks, ensure_ascii=False).encode()).hexdigest()]}}
    quality = {"schema_version": 1, "review_status": "approved",
               "jd_review": {"present": role, "matched_requirement_ids": ["react"] if role else [], "unmatched_requirement_ids": ["mentoring"] if role else []},
               "ats_review": {**{name: True for name in ATS_CHECKS}, "notes": ["Synthetic fixture; not an ATS score or hiring guarantee."]},
               "blocked_claims": [{"claim": "显著提升业务转化率", "reason": "演示输入没有支持该指标的证据"}],
               "blocks": reviews, "copy_approval": {"status": "user_approved", "source": "conversation", "approved_block_ids": list(copy),
               "evidence_quote": "SYNTHETIC QA APPROVAL: approve only this fictional fixture; never copy this into a real user workflow."}}
    jd = None
    if role:
        jd = {"schema_version": 1, "jd_source": {"source_id": "jd-demo", "path": "fictional-jd.txt", "sha256": "a" * 64}, "target_role": "React 前端工程师（虚构岗位）", "organization": "演示组织",
              "requirements": [{"id": "react", "exact_phrase": "维护 React 组件", "normalized_concept": "React", "category": "core_capability", "priority": "high"}, {"id": "mentoring", "exact_phrase": "指导初级工程师", "normalized_concept": "mentoring", "category": "bonus_signal", "priority": "medium"}],
              "matches": [{"jd_item_id": "react", "status": "strong_match", "fact_ids": ["fact-work"], "evidence_ids": ["evidence-work"], "resume_location": "work", "rationale": "输入明确描述 React 组件维护"}, {"jd_item_id": "mentoring", "status": "unmatched", "fact_ids": [], "evidence_ids": [], "resume_location": "not present", "rationale": "没有带教经历证据，不添加此经历"}],
              "unmatched_requirement_ids": ["mentoring"], "clarification_candidates": ["是否有可以核对的带教经历？"], "role_specific_copy_layer_id": "react"}
    return package, quality, jd


def create_workspace(destination: Path, profile="experienced", role=False):
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite {destination}")
    destination.mkdir(parents=True)
    package, quality, jd = fixture(profile, role)
    source = destination / "fictional-package.json"
    source.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    quality_path = destination / "fictional-quality-review.json"
    quality_path.write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    jd_path = None
    if jd:
        jd_path = destination / "fictional-jd-match.json"
        jd_path.write_text(json.dumps(jd, ensure_ascii=False, indent=2), encoding="utf-8")
    write_input(source, destination, quality_review_path=quality_path, jd_report_path=jd_path)
    (destination / "fictional-resume.txt").write_text("\n\n".join(PROFILES[profile].values()), encoding="utf-8")
    return package, quality, jd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--profile", choices=PROFILES, default="experienced")
    parser.add_argument("--role", action="store_true")
    args = parser.parse_args()
    create_workspace(args.destination, args.profile, args.role)
    print(args.destination)


if __name__ == "__main__":
    main()
