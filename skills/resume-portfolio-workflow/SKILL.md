---
name: resume-portfolio-workflow
description: Use when a user wants to turn resume materials into a verified content package and an expressive portfolio site, or when a request must be routed between content work, full website design, and a bounded existing-site change.
---

# Resume Portfolio Workflow

Route work across the plugin's content and website skills while preserving
facts, approvals, plans, and confirmed artifacts.

## Start

1. Read `references/routing-contract.md` completely.
2. Inspect supplied materials, `.resume-site-work/input`, existing
   `build-state.json`, and confirmed artifacts without editing them.
3. Write `.resume-site-work/reports/workflow-route.json`.
4. Run:

```powershell
python "$SKILL_ROOT\scripts\validate_workflow_route.py" `
  ".resume-site-work\reports\workflow-route.json"
```

5. Continue only after validation succeeds.

## Route execution

### content-full

Invoke `resume-content-intelligence`. That skill owns factual inventory,
one-question-at-a-time clarification, content strategy comparison, explicit
strategy approval, implementation planning, final copy approval, and handoff.
After handoff, validate content again before routing to the website skill.

### site-full

Invoke `build-resume-portfolio-site`. That skill owns one-question-at-a-time
design discovery, two or three layout families, explicit site-design approval,
file-level implementation planning, implementation strategy, React source,
preview, snapshots, audits, and motion.

### site-fast-change

Invoke `build-resume-portfolio-site` with the validated route report. Preserve
the confirmed content and design thesis. Edit only the listed files, run the
listed verification, and keep the rollback baseline active until validation
succeeds.

## Boundaries

- Never edit React source or approved content from this orchestration skill.
- Never infer approval from silence, previous confirmation, or an existing
  artifact.
- Never use fast change for new sections, pages, interaction families,
  audience changes, content revisions, or visual-direction changes.
- No external Superpowers skill is required at runtime.
