# Content Package Contract

The skill owns content preparation. The canonical approved handoff consists of:

```text
.resume-site-work/input/source-manifest.json
.resume-site-work/input/normalized-resume.json
.resume-site-work/input/approved-copy.json
.resume-site-work/reports/content-provenance.json
.resume-site-work/reports/content-design-spec.json
.resume-site-work/reports/content-implementation-plan.json
.resume-site-work/reports/content-quality-review.json
.resume-site-work/reports/jd-match.json (when a JD is supplied)
```

`normalized-resume.json` contains source facts and evidence references. `approved-copy.json` contains only copy blocks with `approval_status: user_approved`. The website skill may use the approved copy and normalized facts to create its Stage 1 `content-map.json`; it must not treat draft copy or low-confidence inference as factual input.

The package must remain versioned. A confirmed package may not be overwritten without increasing `handoff.revision` and preserving the previous package in the caller's normal workspace snapshot mechanism.

`content-design-spec.json` records explicit strategy approval.
`content-implementation-plan.json` records evidence-linked work before copy
drafting. Neither report is factual evidence, and strategy approval is not
final copy approval.

`content-quality-review.json` records the writing-coach, STAR, ATS, evidence,
ownership, result, and optional JD checks for every approved experience and
project block. It must pass `scripts/validate_content_quality_review.py` after
explicit conversational copy approval and before `approved-copy.json` is
written. A changed block invalidates its review and approval.

`jd-match.json` remains a separate role-specific report. Each JD requirement
records its exact phrase, normalized concept, category, and priority. Each match
records fact IDs, evidence IDs, resume location, rationale, and one of
`strong_match`, `partial_match`, `transferable`, or `unmatched`. An unmatched row
must reference no fact/evidence IDs and cannot authorize new resume copy.

## Claim rule

Every generated claim must reference at least one evidence ID or have `confirmation_status: user_confirmed`. Missing evidence is a reason to ask the user a question, not a reason to invent a number, title, date, or responsibility.

## Atomic content revisions

Prepare new package, quality review and optional JD report under `.resume-site-work/staging/`. Pass them to `write_resume_site_input.py --package <path> --quality-review <path> --jd-report <path> --workspace-root <workspace>` (omit the JD argument without a JD). For updates, pass a strictly increasing `--revision`. The writer validates the complete candidate, snapshots the old valid handoff, then replaces the files with rollback on failure. Do not overwrite canonical quality/JD reports before this step. Saved revision workspaces live under `versions/content-rN/` and can be validated/restored independently. For named job variants, use [role-versions.md](role-versions.md).
