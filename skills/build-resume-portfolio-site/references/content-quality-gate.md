# Content Quality Gate

Apply this gate to every experience and project copy block after content strategy
and implementation-plan approval, but before writing `approved-copy.json`.

## Required inputs

Read these resources completely before drafting:

- `writing-coach-rules.md`;
- `star-and-impact-rubric.md`;
- `ats-safety-checklist.md`;
- `jd-customization-rules.md` when a JD exists.

Use only normalized facts, evidence, user confirmations, and rows from the
validated `jd-match.json` report. Copy its matched and unmatched requirement IDs
into the quality report without reclassifying them.
An unmatched JD requirement may trigger a clarification question but cannot
authorize a keyword, skill, responsibility, or result in copy.

## Per-block review

For every experience or project block, record:

- the supported action, method, scope, and result treatment;
- fact IDs and evidence IDs for the recommended copy;
- JD requirement IDs actually used in the copy;
- whether ownership, results, and every claim remain supported;
- one recommended version;
- an optional stronger version only when it has its own fact and evidence links.
- the exact selected version (`recommended` or `stronger`) approved by the user.

Use `result.kind=evidenced` only with fact and evidence IDs. When no trustworthy
result evidence exists, use `result.kind=qualitative_fallback`, explain why, and
confirm that unsupported metrics were removed. Put rejected, exaggerated, or
unsupported alternatives in `blocked_claims` rather than weakening the truth
standard.

## Approval and output

Write `.resume-site-work/reports/content-quality-review.json` against
`content-quality-review-schema.json`. Show the proposed copy to the user and wait
for explicit approval of the exact wording. Strategy approval, TODO approval,
browser activity, or a generic request to continue is not copy approval.

After approval, record the conversational approval quote and the exact approved
block IDs. Set `selected_version` to the wording the user approved, then run:

```powershell
python "$SKILL_ROOT\scripts\validate_content_quality_review.py" `
  ".resume-site-work\reports\content-quality-review.json"
```

Write `approved-copy.json` only after this command exits `0`. Any copy change
invalidates the affected block approval and requires a new review and explicit
approval.
