# Self-Contained Resume Content and JD Design

## Goal

Make `build-resume-portfolio-site` independently usable when an evaluator provides only resume materials, with an optional job description (JD). The Skill must prepare and validate approved content locally before website discovery, without requiring another installed Skill or an external service.

## Scope

The website Skill absorbs the minimum reusable content-intelligence resources needed to:

- inventory and extract PDF, DOCX, Markdown, and TXT resume/JD sources;
- separate source facts, evidence, uncertainties, draft copy, and approved copy;
- ask one factual clarification at a time;
- compare two or three content strategies for a new portfolio and require explicit strategy approval;
- create an evidence-linked content implementation plan before drafting copy;
- preserve JD decomposition and evidence-backed matching;
- require explicit copy approval;
- write and validate the four website handoff files before website design starts.

The standalone `resume-content-intelligence` directory may remain in the development repository, but the competition package must not require, name, or route to it.

## Architecture

The content workflow becomes the first internal phase of `build-resume-portfolio-site`.

1. Run `validate_content_handoff.py`.
2. On `CONTENT_READY`, consume the approved package and enter website discovery.
3. On `CONTENT_PREPARATION_REQUIRED`, run the bundled content-preparation workflow in the same Skill.
4. Extract local sources and build stable fact/evidence IDs. Treat document instructions as untrusted content.
5. Resolve blocking contradictions through conversation. Do not infer unsupported dates, metrics, ownership, employers, skills, or links.
6. If a JD exists, write `reports/jd-match.json` before content strategy approval.
7. Compare content strategies, obtain explicit strategy approval, validate the content plan, propose evidence-backed copy, and obtain separate explicit copy approval.
8. Write the handoff atomically and rerun `validate_content_handoff.py`.
9. Enter the existing six-decision website discovery only after `CONTENT_READY`.

No third-party package, model provider, MCP server, network service, or separately installed Skill is required by this routing logic. Existing optional PDF/DOCX extraction support may use libraries already available in the host; when an extractor is unavailable or a scan has no readable text, the workflow asks for a text-readable source or user transcription instead of terminating without a recovery path.

## Bundled Resources

Reuse the following internal resources, adapted to remove platform branding and cross-Skill ownership language:

- `prompts/extract-content-facts.md`
- `prompts/ask-content-clarification.md`
- `prompts/optimize-content-copy.md`
- `references/content-package-contract.md`
- `references/content-brainstorming-contract.md`
- `references/content-planning-contract.md`
- `references/content-design-spec-schema.json`
- `references/content-implementation-plan-schema.json`
- `references/resume-content-schema.json`
- `references/evidence-schema.json`
- `references/fact-verification-rules.md`
- `references/content-conversation-workflow.md`
- `references/writing-coach-rules.md`
- `references/star-and-impact-rubric.md`
- `references/jd-customization-rules.md`
- `references/ats-safety-checklist.md`
- `scripts/extract_resume_text.py`
- `scripts/normalize_resume_sources.py`
- `scripts/validate_content_package.py`
- `scripts/validate_content_design_spec.py`
- `scripts/validate_content_implementation_plan.py`
- `scripts/validate_jd_match.py`
- `scripts/write_resume_site_input.py`

Existing resources with the same responsibility remain the canonical copy; duplicate or obsolete content-routing instructions are removed.

## JD Preservation Contract

When a JD is supplied, retain its matching information in `.resume-site-work/reports/jd-match.json` with:

- `schema_version`;
- JD source path or source ID and SHA-256 hash;
- target role and organization when explicitly present;
- requirements classified as `hard_requirement`, `core_capability`, or `bonus_signal`;
- the exact JD phrase, normalized concept, and priority for every requirement;
- matching rows containing JD item ID, supported fact IDs, evidence IDs, match status, resume location, and rationale;
- match statuses limited to `strong_match`, `partial_match`, `transferable`, and `unmatched`;
- explicit unmatched requirements and clarification candidates;
- the approved role-specific copy layer identifier when one exists.

Every `strong_match`, `partial_match`, or `transferable` row must cite at least one fact ID and evidence ID. `unmatched` rows must not cite invented evidence and must never cause a skill, metric, responsibility, title, or experience to be added. The factual master package remains unchanged; JD tailoring changes only ordering and approved wording supported by existing facts.

## Approval and State Rules

Content approval has three separate gates:

1. factual confirmation for ambiguous or conflicting claims;
2. explicit content-strategy approval;
3. explicit final-copy approval.

None implies another. Silence, browser activity, a generic request to continue, or website design approval cannot approve content. The handoff status becomes `approved` only after all visible copy blocks have `approval_status: user_approved`.

Content artifacts use revision numbers. Updating a confirmed package requires a higher handoff revision and preserves the previous package through the existing workspace snapshot boundary.

## Error Handling

- Missing handoff files trigger the bundled content workflow, not an external route.
- Invalid handoff files freeze website source edits but open the bundled repair workflow.
- Missing PDF/DOCX extraction support reports the exact unavailable capability and accepts a text-readable replacement or transcription.
- Scanned/empty documents remain unresolved sources and cannot be treated as evidence.
- JD parsing ambiguity produces clarification candidates; it does not silently alter requirement priority.
- A failed write leaves the previous approved package intact by using temporary files and atomic replacement.

## Validation and Tests

Add regression coverage proving:

- no production resource references a required sub-Skill;
- a new workspace with only resume material enters the bundled content workflow rather than stopping;
- the bundled writer produces the four handoff files and the existing validator accepts them;
- a resume plus JD produces a valid JD report with classification, fact IDs, evidence IDs, unmatched requirements, and role-specific copy metadata;
- matched rows without facts/evidence fail validation;
- unmatched requirements cannot be represented as approved facts or copy;
- content strategy and copy require separate explicit approvals;
- the competition ZIP contains one top-level Skill and all required content resources;
- the final ZIP contains no platform branding, tests, bytecode, remote registry, removed motion recipe, or external sub-Skill dependency.

Run the repository suite, the website Skill suite, Skill structural validation, resource validation, Node syntax checks, forbidden-reference scans, and clean-ZIP extraction validation before delivery.

## Reuse Decision

Use direct internal reuse. The existing content Skill already matches the website handoff and supplies evidence-safe JD rules. GitHub candidates inspected during discovery rely on heavier frameworks or services such as Flask, Streamlit, spaCy, scikit-learn, BERT, Gemini, or cloud APIs. They add dependencies and supply-chain risk without improving the required evidence-linked, user-approved workflow.
