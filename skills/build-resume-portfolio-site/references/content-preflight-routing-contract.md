# Content Preflight Routing Contract

## Purpose

The website builder is the default entry point, while
`resume-content-intelligence` remains the owner of extraction, fact
verification, copy optimization, JD matching, and content approval. This
preflight selects the correct path before a new Stage 1 build.
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
- Exit `2`, `ROUTE_REQUIRED`: **REQUIRED SUB-SKILL:** Use
  `resume-content-intelligence`, wait for user content approval and handoff,
  then rerun this validator.
- Exit `1`, `CONTENT_INVALID`: do not edit React source, state, preview, or
  snapshots. Use `resume-content-intelligence` to repair or revise the package,
  then rerun validation.

The required handoff is:

```text
.resume-site-work/input/source-manifest.json
.resume-site-work/input/normalized-resume.json
.resume-site-work/input/approved-copy.json
.resume-site-work/reports/content-provenance.json
```

## Consumption rules

Stage 1 derives `content-map.json` only from `normalized-resume.json` and
`approved-copy.json`. Use normalized facts as factual evidence and approved
copy as the visible-copy source. The builder may arrange, shorten, or omit
approved blocks to fit the selected composition, but it must not introduce a
new claim, promote an inference, or silently rewrite approved copy.

A content change requires a higher `handoff.revision`. Never overwrite a
confirmed package in place. Existing website snapshots continue to provide the
normal rollback boundary.
