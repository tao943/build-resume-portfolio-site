# Motion Recipe Schema

The catalog is a short, runtime-safe derivative of the eleven preserved source prompts. Runtime selection reads the manifest and at most one selected recipe; it never injects every source prompt.

Each recipe uses `schema_version: 1` and defines:

- `id`, `source_id`, `name`, and a short `summary`;
- `primary_slot`: `hero_ambient`, `hero_background`, or `hero_content_media`;
- `selection_signals`: concise content and visual cues used for matching;
- `media.requirement`: `none`, `optional`, or `preferred`;
- `media.placement_reference`: a composition hint with `layer`, `fit`, and `description`, never permission to replace the confirmed page composition;
- `media.playback`: always a passive muted loop with `scroll_linked=false` and `pointer_linked=false`;
- `performance`: `medium` or `heavy`;
- `preserve`: the invariants that Stage 5 cannot rewrite.

The selected recipe may alter only the approved motion/media layer. Resume facts, section order, palette, typography, responsive hierarchy, and the source-agnostic confirmed media direction baseline remain unchanged.
