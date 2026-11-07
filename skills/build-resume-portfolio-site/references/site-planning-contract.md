# Site Planning Contract

The active design specification is schema version 4; existing unmigrated v3
specifications remain readable. Follow [interaction-modes.md](interaction-modes.md)
for mode-specific approval. No React edits precede validated design and plans.

## Readable TODO

Create `.resume-site-work/reports/site-todo-plan.md` with concise tasks for
content and structure, design tokens, authorized media, compatible motion,
exact files and component ownership, responsive and accessible behavior,
build and screenshots, bounded repair, rollback, and deliverables.

In quick mode, prepare the TODO alongside the proposed design and obtain one
approval for the whole bundle and delegated execution. Record the unchanged
file's SHA-256 in `bundle_approval.todo_plan_sha256`. In deep mode, prepare the
TODO after requirements approval and obtain explicit approval of the shown
plan. A reply can cover multiple clearly displayed decisions; do not invent
approval for material the user has not seen.

## Execution arrangement

Quick mode lets the Agent choose `single-agent` or `parallel-wave` under the
approved execution delegation, without asking the user to choose technical
implementation details. Choose parallel work only for independently useful,
disjoint file ownership and a demonstrated benefit; otherwise use single-agent.

Deep mode retains an explicit strategy selection if no equivalent authorization
is already present. Explain the recommendation in plain language, and reuse an
existing explicit selection for the unchanged plan. Parallel work always needs
a validated multi-agent plan. If that validation fails, repair the plan or use
single-agent within a quick bundle's delegation; never silently override an
explicit user requirement to use a particular execution mode.

## Machine plan

Write schema-version-2 `reports/site-implementation-plan.json`. Include the
readable plan path and approval, stable task IDs, dependencies, exact writable
files, consumed inputs, produced interfaces, acceptance, verification, rollback
baseline, and `versions/v1-integrated` target. Use
`generation_mode: one-integrated-site`. The selected strategy must match
`strategy_selection.selected`.

Deep mode uses `strategy_selection.status: user_selected`,
`source: explicit_user`, `channel: conversation`. Quick mode uses
`status: agent_selected`, `source: approved_bundle`, `channel: workflow`, and
the current `bundle_id`; see the complete record in the mode reference.

Validate before source edits:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/validate_site_implementation_plan.py" \
  ".resume-site-work/reports/site-implementation-plan.json" \
  --design-spec ".resume-site-work/reports/site-design-spec.json" \
  --workspace-root "."
```

Quick validation checks the approved design and actual TODO file as well as
plan structure. Changed requirements or tasks invalidate the relevant approval;
show the revised scope and obtain approval before regeneration.
