# Screenshot Review Rules

Capture and review these viewports:

| Name | Width | Height |
|---|---:|---:|
| desktop | 1440 | 900 |
| tablet | 1024 | 768 |
| mobile | 390 | 844 |

Every finding records `rule_id`, viewport or state, selector or region,
`evidence_refs`, severity, `contract_path`, permitted files, proposed local
change, and intended observable result. Classify findings as `blocking`,
`repairable`, or `advisory`.

## Separate quality dimensions

Review these dimensions independently:

- **Identity fit:** personal specificity, factual narrative, priority, role and
  domain relevance, and the relationship between content and form.
- **Aesthetic quality:** hierarchy, typography, color coherence, spatial rhythm,
  composition distinctiveness, surface restraint, purposeful motion,
  responsive integrity, and production polish.

A passing identity fit review cannot compensate for failed aesthetic quality.
A passing aesthetic quality review cannot compensate for inaccurate or generic
identity fit. Both reviews cite captures and approved contract paths.

## Deterministic production checks

- Check horizontal overflow, clipping, overlap, broken navigation, console/page
  errors, focus visibility, contrast, readable type, line measure, and heading
  hierarchy.
- Check spacing rhythm, unintended alignment drift, excessive density, image
  cropping, empty space, section transitions, and visual-system consistency.
- Check that rendered copy and factual media still match normalized inputs and
  authorized-media meaning.
- Check that the approved signature protagonist and structural device remain
  visible without depending on motion.
- Check that responsive transformations preserve narrative and visual priority.

## Contextual anti-template checks

Anti-template checks are contract-aware quality detectors, not universal style
bans. Record a failure only when a treatment conflicts with the approved
contract, becomes indiscriminate repetition, or causes an observable quality or
usability defect.

- Detect unrelated content flattened into repeated uniform cards.
- Detect a generic centered hero plus symmetric feature grid when the approved
  contract requires another composition.
- Detect indiscriminate repetition of glass, glow, gradient, pill, radius, or
  shadow treatments.
- Detect a missing visual protagonist or signature structural device.
- Detect motion without a stated content, hierarchy, or navigation purpose.
- Detect responsive collapse that destroys the approved hierarchy or signature.

An intentionally approved card, gradient, glow, pill, radius, or shadow remains
valid when it has a clear role and does not become indiscriminate repetition.

## Dynamic interaction and media states

For every controller family present, audit the initial state and one
representative active state. Record the controller family, trigger, target,
viewport, observed state, and capture references in
`interaction_states_checked`. Controller families include scroll,
pointer/hover, keyboard/focus, click/tap, drag, timed, and media. Record
`not_present` rather than inventing an interaction.

- Audit the coarse-pointer/touch alternative and `prefers-reduced-motion` state.
- Audit media loading, ready, and error states. Poster fallback remains
  meaningful while loading, on error, for reduced motion, and on constrained
  touch/mobile paths.
- Check clipping, focus order, readability, image/UI cohesion, controller conflicts,
  and factual-media integrity in initial and active states.

Essential-content loss, scroll traps, factual-media distortion, absent
fallbacks, and a failed required quality dimension are `blocking`, even when
another viewport or static state looks correct.

Treat clipping, focus order, readability, image/UI cohesion, controller conflicts,
essential-content loss, scroll traps, factual-media distortion, and
absent fallbacks as explicit review markers; the last four are always blocking.

## Repair policy

- Validate `reports/visual-audit.json` against the approved design contract
  before editing.
- Modify only finding-level `permitted_files` and the smallest affected DOM/CSS
  region.
- Preserve approved facts and all unrelated design-contract paths.
- Rebuild and recapture desktop, tablet, mobile, and every affected interaction
  or fallback state after each completed repair.
- Count only completed visual repair rounds; infrastructure retries do not
  consume the two-round limit.
- Preserve the last valid preview when validation, build, capture, or audit fails.
- Stop with `visual_blocked` and evidence when blocking findings remain after
  round two. Present advisory findings without extending the loop.
- Add no confirmation step; successful bounded repair continues automatically.
