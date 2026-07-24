# Screenshot Review Rules

Capture and review these viewports:

| Name | Width | Height |
|---|---:|---:|
| desktop | 1440 | 900 |
| tablet | 1024 | 768 |
| mobile | 390 | 844 |

## Audit categories

Classify every finding as `blocking`, `repairable`, or `advisory` and record its viewport, selector/region, evidence, and proposed local change.

- Check hierarchy, typography, spacing, alignment, contrast, and content density.
- Check image cropping, empty space, section transitions, and visual-system consistency.
- Check horizontal overflow, clipped content, overlapping elements, unreadable text, and broken navigation.
- Check browser console/page errors from `capture-report.json`.
- Check that the rendered copy still matches the normalized resume and portfolio inputs.

## Dynamic interaction and media states

For every controller family present in the page, audit the initial state and one representative active state. Record the controller family, trigger, target, viewport, observed state, and screenshot or capture evidence in `reports/visual-audit.json` under `interaction_states_checked`. A controller family may be scroll, pointer/hover, keyboard/focus, click/tap, drag, timed, or media; record `not_present` rather than inventing a missing interaction.

- Audit the coarse-pointer/touch alternative and the `prefers-reduced-motion` state for every applicable controller.
- Audit media loading, ready, and error states. The Poster fallback must remain meaningful and usable when loading fails, motion is reduced, or the touch/mobile path suppresses playback.
- Check clipping, focus order, readability, image/UI cohesion, and controller conflicts in both the initial and active state.
- Check that active media remains factual: cropping, overlays, generated decoration, and playback must not distort the meaning of a supplied factual image or video.

Classify essential-content loss, scroll traps, factual-media distortion, and absent fallbacks as `blocking`. These failures remain blocking even if another viewport or static state looks correct.

## Repair policy

- Modify only the affected DOM/CSS region.
- Preserve the confirmed StyleBrief and content map.
- Do not rewrite the full page to fix a local defect.
- Re-capture all three viewports after each repair.
- Count only completed visual repair rounds; infrastructure retries do not consume the two-round limit.
- Preserve the last-valid-preview when validation, build, capture, or the dynamic-state audit fails.
- Stop with `visual_blocked` and an explicit defect list when blocking findings remain after round two.
- Do not add a confirmation step; successful repair continues automatically.
