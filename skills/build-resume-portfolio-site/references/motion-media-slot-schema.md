# Motion Media Slot Schema

`reports/motion-media-slot.json` records:

- a stable `media_slot_id` and site-specific `resolved_placement`;
- local `poster_path`, `aspect_ratio`, `fit`, layer, and text-safe area;
- passive `playback` with `scroll_linked=false` and `pointer_linked=false`;
- required `preserve` invariants;
- responsive fallback and reduced-motion behavior.

The resolved placement may move or resize media to fit the confirmed website. It cannot reorder sections, replace copy, change the design system, or create a second hero focal point.
