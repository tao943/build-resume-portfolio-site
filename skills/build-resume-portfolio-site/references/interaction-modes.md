# Interaction modes

Persist `interaction_mode: quick | deep` in `build-state.json`, the design
specification, and the implementation plan. It is independent of
`workflow_mode: full | fast-change`, which describes the scope of a change.
Recommend quick mode for a new user. Honor an expressed preference without
asking again. Existing workspaces without the field retain deep mode; changing
modes never retroactively changes an approval or confirmed artifact.

Both modes preserve factual clarification, approval of exact copy and public
fields, final acceptance, and any separately authorized external publication.
Mode selection alone approves no facts, copy, visual choices, or source edits.

## Quick: one design and execution bundle

1. After `CONTENT_READY`, generate and validate both design baselines. Query the
   five categories using the same baselines and only already approved decisions.
   Initial quick queries can therefore share an empty working-decision file.
   Keep proposed choices tentative; do not invent individual user approvals.
2. Privately compare candidates and choose a compatible recommended combination.
   Keep source IDs, alternatives, responsive fallbacks, and accessibility checks.
   Structure stays Agent-owned. Include an explicit reason if media is skipped.
3. Show one combined design summary and a concise TODO plan with deliverables,
   exact file scope, verification, and rollback. Explain that the Agent will
   choose the execution arrangement. Offer one combined visual preview only
   when the user's preview preference is unknown; reuse the same gallery URL.
4. Receive one conversational approval of the displayed design, TODO plan, and
   delegated execution. The user may revise any choice before approving. Save
   the exact reply and a stable approval ID; generic mode selection is not this
   approval. Save the approved TODO file unchanged and compute its SHA-256.
5. In schema-v4 `site-design-spec.json`, set `interaction_mode: quick` and add:

```json
"bundle_approval": {
  "id": "design-bundle-1",
  "status": "user_approved",
  "source": "explicit_user",
  "channel": "conversation",
  "quote": "<actual reply approving the displayed bundle>",
  "structure_delegated": true,
  "execution_delegated": true,
  "todo_plan": ".resume-site-work/reports/site-todo-plan.md",
  "todo_plan_sha256": "<SHA-256 of the exact displayed TODO file>",
  "selected_candidate_ids": {
    "typography": ["<chosen candidate ID>"],
    "color": ["<chosen candidate ID>"],
    "media": [],
    "primary_motion": ["<chosen candidate ID>"],
    "secondary_motion": ["<chosen candidate ID>"]
  }
}
```

Use `media: []` only for an approved skip. All category and requirements
approvals retain `status: user_approved`, `source: explicit_user`, and
`channel: conversation`, plus `bundle_id` referencing this record. This records
one genuine batch approval; it does not imply separate replies. Accepted
category previews all reference the same session gallery. Validate the spec.

6. Write the implementation plan with `interaction_mode: quick`, the matching
   `bundle_approval_id`, and the same ID in `todo_plan_approval.bundle_id`.
   Choose execution based on task independence and host capabilities; use:

```json
"strategy_selection": {
  "status": "agent_selected",
  "source": "approved_bundle",
  "channel": "workflow",
  "bundle_id": "design-bundle-1",
  "selected": "single-agent",
  "recommended": "single-agent",
  "reasons": ["Shared component ownership makes parallel work unnecessary."]
}
```

A parallel choice still needs authorized delegation and a validated disjoint
multi-agent plan. Validate the plan with `--design-spec` and `--workspace-root`.
The validator checks approval linkage, selected IDs, and the TODO file hash.
Changed selections or plan content invalidate this bundle before source edits.
Content-copy approval is separate and is never created by this process.

## Deep: category review

Keep the five category-by-category selections and requirements/TODO review.
Reuse the user's explicit browser preference for its stated scope. A request
for previews throughout discovery needs no repeated permission question; a
single-category acceptance does not imply broader consent. Reuse one session
URL and refresh its gallery, rather than opening new windows. A user can change
preview preference or switch mode at any time. Preserve already approved facts
and categories; reapprove only decisions affected by the change.
