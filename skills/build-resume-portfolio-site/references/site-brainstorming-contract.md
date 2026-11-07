# Site Brainstorming Contract

Use full discovery for a new site or a change to audience, structure, visual
thesis, or interaction architecture. Read [interaction-modes.md](interaction-modes.md)
for quick versus deep review. Both modes use the same design quality checks.

Build a privacy-safe content map from approved content, then validate the
three-direction database baseline and provisional anti-template baseline.
The latter identifies the visual protagonist, content-to-form thesis,
signature devices, and one evidence-linked obligation per category. It has
`status=provisional_unapproved` and cannot authorize React edits.

Structure is Agent-delegated. After planning, compare `fit`, `novelty`, and
`wildcard` privately; do not add a structure selection gate. Query typography,
color, media, primary motion, and secondary motion from the vendored catalog.
Each candidate needs source IDs, fit/risk/tradeoffs, compatibility, responsive
fallbacks, and accessibility notes. Fewer than two complete candidates blocks
selection as `design_catalog_insufficient`; do not fabricate catalog results.

In deep mode, query and approve categories in that order. Each query inherits
all previous approved decision IDs. In quick mode, query against the common
baselines using only decisions already approved before the bundle; compare the
combined compatibility internally and present a single recommended bundle.
Tentative choices never appear as approved inherited IDs.

Use one primary-motion system and any compatible secondary effects. Skip
media only with a recorded reason included in the category or bundle approval.
Responsive behavior, keyboard access, coarse-pointer support, media fallbacks,
and reduced motion remain mandatory. Present any conflict with the
anti-template baseline as a trade-off; a conflicting candidate cannot be the
default recommendation.

Apply [visual-style-preview-contract.md](visual-style-preview-contract.md).
Preview consent is separate from design approval, but can cover all discovery
when explicitly stated. A visit, reload, or screenshot never approves a choice.

A core decision change invalidates affected downstream evidence and approvals.
In deep mode, rerun downstream queries with the changed inherited IDs. In quick
mode, rebuild the proposed bundle and its TODO, then obtain a new batch approval.
Changes to content, audience, baseline direction, visual protagonist, or
content-to-form thesis invalidate both the provisional baseline and dependent
category reports. Never edit React source before approved requirements and a
validated implementation plan. Existing bounded edits use the fast-change
route with confirmed source, exact files, verification, and rollback.
