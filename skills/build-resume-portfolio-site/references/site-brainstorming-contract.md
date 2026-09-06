# Site Brainstorming Contract

Use the full workflow for a new site or any change to audience, structure,
visual thesis, interaction architecture, or implementation strategy.

## Required decision order

Inspect approved content, authorized media, references, existing state, and
confirmed artifacts before asking questions. Build and validate the privacy-safe
content map, then query the vendored design catalog for a three-direction
baseline. Before the first question, compile and validate the provisional
anti-template baseline that states the candidate visual protagonist,
content-to-form thesis, composition hypothesis, signature devices, template
independence claim, contextual failure rules, and one obligation per category.
Ask one decision-bearing question at a time and complete these decisions in
order:

1. **Overall structure** — composition, hierarchy, navigation, and content density.
2. **Typography** — type character, scale, rhythm, and reading texture.
3. **Color system** — background, foreground, accent, contrast, and semantic roles.
4. **Media treatment** — framing, cropping, sequencing, and fallback. Skip only
   when no authorized media exists and the user does not want a media strategy;
   record an explicit reason.
5. **Primary motion** — select exactly one dominant temporal or scroll system.
6. **Secondary motion** — allow multiple effects after filtering compatibility
   with the primary system, controller ownership, performance, mobile,
   coarse-pointer, cleanup, fallback, and reduced motion.
7. **Final requirements confirmation** — summarize every enabled decision and
   mandatory engineering constraint, then obtain explicit conversational approval.
8. **TODO plan approval** — follow `site-planning-contract.md`; do not edit React
   source until the readable plan is explicitly approved and the JSON plan validates.

Responsive behavior, accessibility, coarse-pointer support, media fallbacks,
and reduced motion are requirements, not optional style choices.

## Per-category transaction

For each enabled category:

1. Set `design_<category>_querying`. Query the category's required catalog
   domains using the database baseline, the provisional anti-template baseline,
   and every prior conversationally approved decision ID. Write and validate
   `reports/design-discovery/<category>.json` before showing candidates.
2. If retrieval returns fewer than two complete candidates or any candidate
   lacks `source_ids`, stop with `design_catalog_insufficient`; do not synthesize
   a database candidate.
3. Set `design_<category>_selecting`. Compare two or three materially different candidates, except secondary
   motion may offer more compatible effects without a fixed numeric cap.
4. Recommend one candidate or compatible set and state fit, risk, trade-offs,
   compatibility, responsive fallback, accessibility notes, catalog source IDs,
   and whether it strengthens, preserves, or conflicts with the anti-template
   baseline. A conflicting candidate may be shown as a labeled trade-off but
   cannot be the default recommendation.
5. Ask whether to open the browser comparison in a separate message before
   requesting a choice for this category.
6. If accepted, follow `visual-style-preview-contract.md`; if declined, record
   `not-requested` and continue text-only.
7. Receive the user's selection in the conversation after the preview or
   decline.
8. Receive explicit confirmation, revision, or rejection in the conversation.
9. Lock the decision, its discovery report, and selected source-linked IDs in
   `design-decisions-working.json` before entering the next category.

An accepted preview produces a display-only `gallery.html` outside the React
source project.

Prior browser consent does not apply to later categories. Browser activity never counts as approval
and never advances state. It also never counts as selection. Do not repeatedly
offer a category after the user declines its preview. When media is explicitly
skipped, record the reason and do not offer a media preview.

The user-selected domain sequence is typography=`typography/style/ux`, color=`color/style/ux`,
media=`style/product/landing/ux`, primary motion=`motion/style/landing/ux`, and
secondary motion=`motion/react/ux`. Each query inherits both baselines and all
prior approved decision IDs; it never uses names, contact details, raw resume
paragraphs, or project secrets. The provisional baseline has
`status=provisional_unapproved`: browser activity, preview consent, and the
artifact itself never select or approve a category.

Structure is recorded as Agent-delegated and is selected privately from two
feasible seed-derived directions plus one wildcard after planning. It receives
the same provisional anti-template obligations but adds no structure preview or
approval gate.

After final requirements confirmation, write schema-version-4
`.resume-site-work/reports/site-design-spec.json` and validate it before
planning. A changed core decision invalidates only downstream category reports,
final requirements approval, TODO approval, and the implementation plan. Rerun
those downstream database queries with the revised inherited choices.
Changing content, audience, the selected baseline direction, visual
protagonist, or content-to-form thesis invalidates the provisional baseline and
all six downstream reports.

Do not create or edit React source during discovery or planning.

Fast change is allowed only with a validated workflow route, a confirmed
artifact, exact affected files, verification, and rollback baseline. If scope
expands, return to the full workflow.
