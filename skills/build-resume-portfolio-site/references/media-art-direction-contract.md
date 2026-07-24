# Media Art Direction Contract

## Purpose and inputs

Media art direction turns the confirmed prototype into one coherent implemented winner without changing confirmed content, hierarchy, facts, or project boundary. It consumes the confirmed prototype, normalized facts, authorized media inventory, optional StyleBrief and reference evidence, design intelligence, and rejected direction IDs. It produces `reports/media-art-direction.json` at schema version `1` and one implemented winner in the same React + Vite project.

Authorized user-provided media is evidence, not decorative raw material. Before composing, write `reports/media-inventory.json` with an `assets` array. Each asset has a stable `id`, `factual_meaning`, and non-empty `immutable_facts`; `role` and `source` are optional. This inventory is the trusted source for report validation, not `image_analysis`. Before composing, inspect each image or video and record its image role, factual meaning, caption or source context, people, product state, chronology, and other immutable facts. Keep factual media recognizable and do not use cropping, generated substitutes, filters, animation, or juxtaposition to alter factual meaning.

## Decision recipe

1. Inspect UI and media inventory; assign image roles and immutable facts.
2. Privately draft multiple directions and compare beauty, content, narrative, coherence, device fit, and delivery risk.
3. Select one best candidate and write `reports/media-art-direction.json` before source edits.
4. Implement the winner in the same React + Vite project, then validate/build and show one interactive candidate.
5. Preserve the last valid preview if a later experiment fails validation.

The report contains at least two internal directions, one selected direction ID that matches an internal direction, and at least one section direction. The portable JSON Schema validates report shape; a deterministic workflow validator enforces selected-ID membership and requires non-empty `image_analysis` whenever the trusted inventory contains authorized media. Every report image ID must exist in `reports/media-inventory.json`, and each factual meaning and immutable-fact set must match its trusted asset after whitespace normalization. `image_analysis` may be empty only when the inventory has no assets. Internal directions remain private unless the user requests the comparison.

## Composition vocabulary and visual rhythm

Use approved vocabulary only where it serves the story: image, gallery, card, scroll, video, CSS-3D, and WebGL. Compositions can include 3D Coverflow, Dome Gallery, Hover Image Trail, Sticky Stack, editorial gallery, card grid, scroll narrative, video sequence, CSS-3D plane, or restrained WebGL. These are options, not quotas; there is no numeric effect cap.

Plan a visual energy curve across the page: quiet orientation, rising evidence, a deliberate peak, and release. Each section declares purpose so its energy supports reading order. Image role guides scale, crop, layering, and cadence: a proof image needs legibility, while a supporting texture may sit behind copy.

## Interaction ownership and conflict resolution

Every interactive section declares structured controller ownership: a controller ID, controller type, controlled targets, controlled properties, handoff decision, and conflict-resolution decision. Valid controller types are `scroll`, `pointer`, `drag`, `camera`, `video_progress`, `transform`, and `filter`. `interaction_compatibility` contains structured `{controller, owners, resolution}` records, never free-form strings. One property has one active controller: a scroll timeline cannot also write the same transform as pointer hover; a camera cannot fight drag for the same view; `video_progress` cannot compete with scroll for playback. Split layers or explicitly hand off ownership when needed. Duplicate target/property ownership is valid only when every owner has both explicit handoff and conflict-resolution text.

Conflict resolution is: preserve readable content and user intent; honor reduced-motion and device fallback; keep the primary controller; then remove or simplify the competing effect. Never keep an effect only because it is technically possible.

## Device, motion, and media safety

Distinguish 2.5D CSS depth from real 3D. 2.5D uses layered transforms and retains a usable flat composition. Real 3D (CSS-3D or WebGL) needs a stable non-3D fallback, must not hide core facts in camera-dependent views, and degrades on unsupported hardware.

For a coarse pointer or touch device, replace hover-only interactions with visible states, tap or drag controls, or a static gallery. Under `prefers-reduced-motion`, stop autonomous, parallax, and scroll-scrubbed movement, present a meaningful video sequence frame or poster, and retain factual media and reading order.

Responsive and reduced-motion fallbacks belong to every section direction. User-provided media, captions, source facts, and text alternatives remain available in every fallback. Media upgrades may improve delivery but never replace authorized factual evidence without approval.
