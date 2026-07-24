---
name: resume-content-intelligence
description: Extract, verify, and optimize resume content through Codex conversation before generating a personal portfolio site. Use when Codex needs to read PDF/DOCX/Markdown/TXT resume material, separate facts from inference, ask targeted clarification questions, rewrite experience/project copy with evidence, prepare a confirmed content package, or hand content to build-resume-portfolio-site.
---

# Resume Content Intelligence

Prepare trustworthy resume content before the website builder runs. Keep source facts, evidence, questions, draft copy, and user-approved copy separate.

## Workflow

1. Read `references/content-package-contract.md`, `references/fact-verification-rules.md`, `references/conversation-workflow.md`, and `references/writing-coach-rules.md`. If a JD is supplied, also read `references/jd-customization-rules.md` and `references/ats-safety-checklist.md`.
2. Inventory supplied files without changing them. For local files, run `scripts/extract_resume_text.py`; for a folder, run `scripts/normalize_resume_sources.py`.
3. Build a factual inventory from source text. Attach stable fact IDs and evidence IDs. Mark uncertain or contradictory fields as `needs_clarification`.
4. Present the inventory briefly, then ask one question at a time. Prioritize questions that affect identity, dates, role scope, project outcomes, or factual metrics.
5. After each answer, update the fact status. Do not silently change a fact because a rewrite would sound better.
6. Propose concise copy variants using `references/writing-coach-rules.md`. Check each project with the technical STAR rubric: problem/context, task, action/method, and result. Every claim must cite evidence or explicit user confirmation.
7. If the user provides a JD, build a keyword-to-fact matching matrix. Separate hard requirements, core capabilities, and bonus signals; reorder and rewrite only from supported facts. Keep unmatched requirements visible instead of filling them in.
8. Ask the user to approve the proposed copy. Store only approved copy under `approved_copy` with `approval_status: user_approved`.
9. Run `scripts/validate_content_package.py` before handoff. Then run `scripts/write_resume_site_input.py` to create `.resume-site-work\input\source-manifest.json`, `.resume-site-work\input\normalized-resume.json`, `.resume-site-work\input\approved-copy.json`, and `.resume-site-work\reports\content-provenance.json` for `build-resume-portfolio-site`.
10. Tell the user the content package is ready and invoke `build-resume-portfolio-site` only after content approval.

## Boundaries

- Use the active Codex model for conversation and rewriting; do not require Anthropic, Together, or ResumeHQ MCP credentials.
- Do not invent metrics, employers, titles, dates, skills, links, or media.
- Do not create or edit React/Vite source; the website skill owns `.resume-site-work\site`.
- Do not run job discovery, cloud ATS/HR scoring, or application tracking in this skill.
- If a PDF is scanned or has no extractable text, report it and ask for a text-readable source or user-provided transcription.
- Do not treat general ATS statistics, keyword counts, or one-page advice as facts about a specific employer.
- Do not add a JD keyword unless the user's evidence supports the underlying skill or the user explicitly confirms it.

## References

- `references/conversation-workflow.md`: question ordering and approval gates.
- `references/fact-verification-rules.md`: evidence and contradiction policy.
- `references/writing-coach-rules.md`: provider-neutral copy improvement rules.
- `references/star-and-impact-rubric.md`: technical STAR and evidence-quality review.
- `references/jd-customization-rules.md`: optional JD parsing, keyword tiers, and matching matrix.
- `references/ats-safety-checklist.md`: ATS-friendly structure without keyword stuffing or unsupported claims.
- `references/content-package-contract.md`: handoff files and schema.
