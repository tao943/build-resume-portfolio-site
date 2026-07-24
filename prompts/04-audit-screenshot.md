---
resource_id: audit-screenshot
resource_version: 1
resource_status: ready
output_contract: visual-audit-json
---

# Audit screenshots, dynamic interactions, and media fallbacks

Audit the successful built preview without redesigning it. Capture desktop, tablet, and mobile as specified by `references/screenshot-review-rules.md`, inspect `capture-report.json`, and write `reports/visual-audit.json` before making any repair.

## Required audit evidence

`visual-audit.json` must record the viewport, selector or region, evidence, severity, and local repair proposal for every finding. It must also include an `interaction_states_checked` array. For each controller family, capture and record:

- the initial state and one representative active state;
- the controller family, target, trigger, captured viewport, and state-specific evidence;
- the coarse-pointer/touch alternative and the reduced-motion state.

Controller families include scroll, pointer/hover, keyboard/focus, click/tap, drag, timed, and media controllers when present. Do not invent an interaction solely for the audit; record `not_present` where the controller family is absent.

Exercise every media region in its media loading, ready, and media error state. Confirm a Poster fallback remains visible, meaningful, and usable while media loads, after an error, for reduced-motion, and where the coarse-pointer/touch alternative suppresses playback or costly interaction.

## Findings and repair decision

Check the visual and behavioral categories in the review rules, including clipping, focus order, readability, image/UI cohesion, controller conflicts, and the rendered source facts. Treat essential-content loss, scroll traps, factual-media distortion, and absent fallbacks as blocking. Record blocking defects even when a static screenshot appears acceptable.

For repairable or blocking defects, make only local React/CSS changes. Preserve the confirmed media direction, content, and last-valid-preview: validate, build, promote, and recapture only after a candidate succeeds. A failed repair must leave the last-valid-preview active.

Keep the existing automatic repair loop and its two completed-round limit. This audit adds no user confirmation step: continue automatically when there are no blocking findings, or retain the last-valid-preview and report unresolved blocking defects after round two.
