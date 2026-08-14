# Content Preflight Routing Contract

## Purpose

This Skill owns extraction, fact verification, copy optimization, JD matching,
content approval, and website generation. This preflight selects either the
bundled content-preparation phase or website discovery before React generation.
It is not a website stage or confirmation gate.

## When to run

Run content preflight when:

- starting a new portfolio from resume or portfolio material;
- receiving a new resume, JD, content claim, or factual correction;
- the user asks to revise website copy or resume facts.

Skip it when the task is to resume an existing confirmed site after prototype
confirmation and the requested changes are only visual, media, motion,
responsive, accessibility, or frontend behavior changes. Preserve the
confirmed content baseline in that case.

## Command and outcomes

Run from the active workspace:

```powershell
python "$SKILL_ROOT\scripts\validate_content_handoff.py" --workspace-root "."
```

- Exit `0`, `CONTENT_READY`: consume the approved package directly.
- Exit `2`, `CONTENT_PREPARATION_REQUIRED`: run the bundled content workflow,
  wait for explicit content-strategy and copy approvals, write the handoff, then
  rerun this validator.
- Exit `1`, `CONTENT_INVALID`: do not edit React source, state, preview, or
  snapshots. Repair or revise the package with the bundled content workflow,
  then rerun validation.

The required handoff is:

```text
.resume-site-work/input/source-manifest.json
.resume-site-work/input/normalized-resume.json
.resume-site-work/input/approved-copy.json
.resume-site-work/reports/content-provenance.json
.resume-site-work/reports/content-design-spec.json
.resume-site-work/reports/content-implementation-plan.json
.resume-site-work/reports/content-quality-review.json
```

The quality review must pass `scripts/validate_content_quality_review.py`, and
its reviewed block IDs must exactly match the keys in `approved-copy.json`.

When a JD is supplied, also write and validate
`.resume-site-work/reports/jd-match.json`. It is a role-specific matching layer,
not a source of new facts. Content preflight compares its matched and unmatched
requirement IDs with `content-quality-review.json` before returning
`CONTENT_READY`.

## Consumption rules

Stage 1 derives `content-map.json` only from `normalized-resume.json` and
`approved-copy.json`. Use normalized facts as factual evidence and approved
copy as the visible-copy source. The builder may arrange, shorten, or omit
approved blocks to fit the selected composition, but it must not introduce a
new claim, promote an inference, or silently rewrite approved copy.

A content change requires a higher `handoff.revision`. Never overwrite a
confirmed package in place. Existing website snapshots continue to provide the
normal rollback boundary.
