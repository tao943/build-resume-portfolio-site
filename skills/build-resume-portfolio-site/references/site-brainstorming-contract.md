# Site Brainstorming Contract

Use the full workflow for a new site or any change to audience, structure,
visual thesis, interaction architecture, or implementation strategy.

## Required decision order

Inspect approved content, authorized media, references, existing state, and
confirmed artifacts before asking questions. Ask one decision-bearing question
at a time and complete these decisions in order:

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

1. Compare two or three materially different candidates, except secondary
   motion may offer more compatible effects without a fixed numeric cap.
2. Recommend one candidate or compatible set and state fit, risk, and trade-offs.
3. Receive a tentative selection in the conversation.
4. Ask in a separate message whether to open the browser for this category.
5. If accepted, follow `visual-style-preview-contract.md`; if declined, record
   `not-requested` and continue text-only.
6. Receive explicit confirmation, revision, or rejection in the conversation.
7. Lock the decision before entering the next category.

An accepted preview produces a display-only `gallery.html` outside the React
source project.

Prior browser consent does not apply to later categories. Browser activity never counts as approval and never advances state. Do not repeatedly offer a category after the user declines its preview.

After final requirements confirmation, write schema-version-3
`.resume-site-work/reports/site-design-spec.json` and validate it before
planning. A changed core decision invalidates final requirements approval and
all downstream planning artifacts.

Do not create or edit React source during discovery or planning.

Fast change is allowed only with a validated workflow route, a confirmed
artifact, exact affected files, verification, and rollback baseline. If scope
expands, return to the full workflow.
