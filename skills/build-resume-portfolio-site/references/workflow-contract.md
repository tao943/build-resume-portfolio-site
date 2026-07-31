# Workflow Contract

Persist state after every transition. Never infer approval from silence,
browser activity, or approval of another category.

## Full workflow state machine

```text
content_preflight
-> design_structure_selecting
-> design_typography_selecting
-> design_color_selecting
-> design_media_selecting OR design_media_skipped
-> design_primary_motion_selecting
-> design_secondary_motion_selecting
-> requirements_waiting_confirmation
-> todo_plan_generating
-> todo_plan_waiting_confirmation
-> integrated_generating
-> integrated_auditing
-> integrated_waiting_confirmation
```

Every enabled design state contains tentative selection, a separate browser
preview offer, optional independent Gallery presentation, and explicit
conversational confirmation. A decline affects only that category.

`requirements_waiting_confirmation --confirm--> todo_plan_generating` writes
the schema-v3 design specification. `todo_plan_waiting_confirmation --approve-->
integrated_generating` is allowed only after the readable Markdown plan is shown
and schema-v2 JSON plan validates.

## Integrated transaction

The integrated transaction is the first React generation:

1. Restore the empty/new baseline or the last confirmed artifact for regeneration.
2. Consume approved content, six decisions, readable TODO plan, JSON plan,
   design intelligence, and authorized-media inventory.
3. Edit only `.resume-site-work/site`.
4. Apply structure, typography, color, media, primary motion, and compatible
   secondary motion together.
5. Validate with `--stage integrated`, run `npm run build`, then atomically
   promote the successful `dist`.
6. Capture desktop/tablet/mobile, interaction, coarse-pointer, and
   reduced-motion states; inspect layout, console, accessibility, and fallbacks.
7. Permit at most two bounded repair rounds.
8. Snapshot successful source to `versions/v1-integrated` or a retry suffix.

A failed validation, build, or capture never replaces the last valid preview.

## Final acceptance state machine

```text
integrated_waiting_confirmation --当前效果满意，完成--> complete
integrated_waiting_confirmation --加强动效--> motion_enhancing
motion_enhancing --validate/build/capture--> integrated_waiting_confirmation
integrated_waiting_confirmation --提出修改 and bounded--> integrated_repairing
integrated_repairing --validate/build/capture--> integrated_waiting_confirmation
integrated_waiting_confirmation --提出修改 and core reversal--> affected design state
```

Motion enhancement preserves content, structure, typography, color, and media treatment. It may revise only primary/secondary motion plans and implementation.
A core reversal invalidates that decision's downstream evidence, final
requirements approval, TODO plan approval, and JSON implementation plan.

## Content preflight

Run content preflight before a new site and whenever a resume, JD, factual
claim, or copy revision enters scope. `CONTENT_READY` continues;
`ROUTE_REQUIRED` invokes `resume-content-intelligence` and waits for its approved
handoff; `CONTENT_INVALID` freezes all website artifacts until repaired.

## Planning and strategy

`site-design-spec.json` schema v3 is the user-approved requirements package.
`site-todo-plan.md` is the readable plan explicitly approved in the
conversation. `site-implementation-plan.json` schema v2 is the validated
machine plan. All three precede React edits.

Use `single-agent`, or an explicitly authorized and validated
`fresh-agent-sequential`/`parallel-wave` plan. The main agent owns integration,
shared files, state, preview promotion, snapshots, and publication.

## Fast change

`site-fast-change` requires a confirmed artifact, exact files, verification,
and rollback baseline. Any change to facts, audience, structure, visual thesis,
or interaction architecture returns to full discovery.

## Rollback and failure

- Preview failure falls back to the authenticated URL, static Gallery, or
  text-only confirmation without affecting later offers.
- Planning failure prevents source edits.
- Integrated failure retains the previous valid preview and snapshot.
- Motion enhancement starts from the last valid integrated snapshot.
- Core-decision change invalidates only that decision and downstream artifacts.
- `resource_blocked`, `artifact_invalid`, `build_failed`, and `visual_blocked`
  retain exact diagnostics and never present stale output as current.

## State compatibility

Build-state schema version `4` remains active. Older confirmed artifacts may use
a validated bounded fast-change route. Schema-version-2 design reports remain
readable evidence but do not satisfy new full discovery; schema-version-1 plans
do not satisfy TODO plan approval. Never fabricate migrated approvals.

## Optional APIHz media transaction

APIHz search and later local-video upgrades do not change the current portfolio
stage, discovery or planning gates, approvals, or snapshot baseline. Candidate
search remains outside the React project; selected-only import is explicit.
Provider failure is isolated and the normal workflow remains available. Video
failure restores the confirmed integrated artifact and leaves approvals
unchanged.
