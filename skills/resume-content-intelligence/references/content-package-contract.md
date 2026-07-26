# Content Package Contract

The skill owns content preparation and writes only these files:

```text
.resume-site-work/input/source-manifest.json
.resume-site-work/input/normalized-resume.json
.resume-site-work/input/approved-copy.json
.resume-site-work/reports/content-provenance.json
.resume-site-work/reports/content-design-spec.json
.resume-site-work/reports/content-implementation-plan.json
```

`normalized-resume.json` contains source facts and evidence references. `approved-copy.json` contains only copy blocks with `approval_status: user_approved`. The website skill may use the approved copy and normalized facts to create its Stage 1 `content-map.json`; it must not treat draft copy or low-confidence inference as factual input.

The package must remain versioned. A confirmed package may not be overwritten without increasing `handoff.revision` and preserving the previous package in the caller's normal workspace snapshot mechanism.

`content-design-spec.json` records explicit strategy approval.
`content-implementation-plan.json` records evidence-linked work before copy
drafting. Neither report is factual evidence, and strategy approval is not
final copy approval.

## Claim rule

Every generated claim must reference at least one evidence ID or have `confirmation_status: user_confirmed`. Missing evidence is a reason to ask the user a question, not a reason to invent a number, title, date, or responsibility.
