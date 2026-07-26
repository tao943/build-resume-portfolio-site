# Resume Portfolio Routing Contract

The orchestration skill chooses one route before either domain skill mutates
workspace artifacts.

## Routes

```text
new or changed facts/copy/JD -> content-full
ready content + new/structural/strategic website work -> site-full
ready content + confirmed site + bounded local edit -> site-fast-change
```

Write the decision to
`.resume-site-work/reports/workflow-route.json` and validate it with
`scripts/validate_workflow_route.py`.

## Full workflow

Full routes inspect existing evidence and state, ask one decision-bearing
question at a time, compare two or three materially different approaches,
recommend one, obtain explicit design approval, and validate an implementation
plan before implementation.

## Fast change

Fast change is allowed only when facts, audience, structure, visual thesis, and
interaction architecture remain unchanged. Record exact affected files,
verification, and rollback baseline. If the request expands, return to the
appropriate full route before further edits.

## Ownership

The orchestrator owns routing only. It never rewrites approved content, edits
React source, promotes previews, creates snapshots, or infers approval.
