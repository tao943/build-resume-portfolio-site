# Workflow Contract

Persist state after every transition. Never infer approval from silence,
browser activity, or approval of another category.

## Full workflow state machine

```text
content_preflight
-> content_inventory (when preparation is required)
-> content_clarification
-> content_strategy_waiting_confirmation
-> content_plan_generating
-> content_copy_waiting_confirmation
-> design_structure_selecting
-> design_typography_selecting
-> design_color_selecting
-> design_media_selecting OR design_media_skipped
-> design_primary_motion_selecting
-> design_secondary_motion_selecting
-> requirements_waiting_confirmation
-> todo_plan_generating
-> todo_plan_waiting_confirmation
-> implementation_strategy_waiting_confirmation
-> implementation_plan_generating
-> design_contract_compiling
-> integrated_generating
-> integrated_auditing
-> integrated_waiting_confirmation
```

Every enabled design state compares candidates and offers its separate browser
comparison before user selection. An optional independent Gallery supports the
decision; selection and confirmation happen afterward in the conversation. A
decline affects only that category.

Missing or invalid content stays inside this Skill. The bundled content phase
establishes fact/evidence records, optional JD matching, explicit strategy
approval, a validated content plan, and explicit copy approval. Only a validated
`CONTENT_READY` handoff transitions to website design. JD `unmatched` items stay
unmatched unless the user supplies evidence; they never become generated facts.

`requirements_waiting_confirmation --confirm--> todo_plan_generating` writes
the schema-v3 design specification. Then:

```text
todo_plan_waiting_confirmation --approve--> implementation_strategy_waiting_confirmation
implementation_strategy_waiting_confirmation --choose 1--> implementation_plan_generating
implementation_strategy_waiting_confirmation --choose 2--> implementation_plan_generating
implementation_strategy_waiting_confirmation --choose 2 and unsafe--> implementation_strategy_waiting_confirmation
implementation_plan_generating --plan validates--> design_contract_compiling
design_contract_compiling --contract validates--> integrated_generating
design_contract_compiling --contract invalid--> artifact_invalid
```

Silence, browser activity, inferred preference, or prior approval cannot select
the strategy. Do not write the machine plan or edit React source while waiting.
Do not spawn agents while waiting. Parallel choice requires a validated disjoint plan; failure
returns to the strategy gate without automatic fallback.

## Integrated transaction

The integrated transaction is the first React generation:

1. Restore the empty/new baseline or the last confirmed artifact for regeneration.
2. Consume approved content, six decisions, readable TODO plan, JSON plan,
   design intelligence, creative direction, and authorized-media inventory.
3. Compile and validate `reports/design-contract.json`; this internal artifact
   adds no approval gate and must precede the first React source edit.
4. Edit only `.resume-site-work/site` and obey the validated design contract.
5. Apply structure, typography, color, media, primary motion, and compatible
   secondary motion together.
6. Validate with `--stage integrated`, run `npm run build`, then atomically
   promote the successful `dist`.
7. Capture desktop/tablet/mobile, interaction, coarse-pointer, and
   reduced-motion states; inspect identity fit and aesthetic quality separately
   plus layout, console, accessibility, anti-template rules, and fallbacks.
8. Validate `reports/visual-audit.json` against `reports/design-contract.json`.
9. Permit at most two evidence-linked bounded repair rounds.
10. Snapshot successful source to `versions/v1-integrated` or a retry suffix.

A failed validation, build, or capture never replaces the last valid preview.
Identity fit cannot compensate for failed aesthetic quality, and aesthetic
polish cannot compensate for generic or inaccurate identity fit.

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
`CONTENT_PREPARATION_REQUIRED` invokes the bundled content workflow and waits for
its approved handoff; `CONTENT_INVALID` freezes all website artifacts while the
same bundled workflow repairs the package.

## Planning and strategy

`site-design-spec.json` schema v3 is the user-approved requirements package.
`site-todo-plan.md` is the readable plan explicitly approved in the
conversation. `site-implementation-plan.json` schema v2 is the validated
machine plan. All three precede React edits.

Use `single-agent`, or an explicitly authorized and validated `parallel-wave`
plan. The main agent owns integration, shared files, state, preview promotion,
snapshots, and publication.

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
