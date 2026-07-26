---
resource_id: direct-media-art
resource_version: 1
resource_status: ready
output_contract: react-vite-project-update-and-media-art-direction-json
---

# Direct the media art direction

Direct media art for an already confirmed portfolio prototype. Consume the confirmed prototype, normalized facts, authorized media inventory, optional StyleBrief and reference evidence, `reports/design-intelligence.json`, and rejected direction IDs; reference evidence has priority over Catalog aesthetics when references exist. Preserve the confirmed content model and work inside the same React + Vite project.

Before source edits, inspect UI and each media item. Always write `reports/media-inventory.json` as the trusted authorization input before validating the report: use `{"schema_version": 1, "assets": []}` when no media is authorized. For each authorized item, record factual meaning, immutable facts, and image role. Treat user-provided media as protected evidence: do not crop, filter, animate, replace, or juxtapose it in a way that changes factual meaning.

Privately produce at least two internal directions. Compare beauty, content, narrative, coherence, device fit, and delivery risk. Select one best candidate, explain why, then write `reports/media-art-direction.json` with schema version `1` before implementation. `design_read` is an object with `page_kind`, `audience`, and `vibe`; `responsive_strategy` is an object with meaningful `desktop`, `tablet`, `mobile`, and `coarse_pointer` decisions; `reduced_motion_strategy` is an object with `trigger`, `replacement`, and `content_visibility`. Identify the selected internal direction, include a visual energy curve, and give a section direction for every changed composition. The portable JSON Schema validates shape; the deterministic workflow validator verifies that the selected ID belongs to the internal directions and that every report uses the explicit trusted inventory.

Use the approved vocabulary only where it serves the story: image, gallery, card, scroll, video, CSS-3D, and WebGL. Candidate patterns may include 3D Coverflow, Dome Gallery, Hover Image Trail, Sticky Stack, a video sequence, or an editorial gallery. These are options, not a checklist: there is no numeric effect cap.

For every section, specify interaction ownership with a controller ID and type (`scroll`, `pointer`, `drag`, `camera`, `video_progress`, `transform`, or `filter`), controlled targets and properties, plus an explicit handoff and conflict-resolution decision. Ensure no two controllers write the same property at once. Resolve conflicts by protecting readability and user intent first, then accessibility and device fallback, then the primary interaction; simplify a conflicting effect when necessary.

Plan a visual energy curve from quiet orientation through evidence and a peak to release. Make 2.5D and real 3D optional enhancements with readable flat fallbacks. On a coarse pointer or touch device, do not rely on hover: expose state, provide tap or drag alternatives, or use a static composition. Under `prefers-reduced-motion`, remove autonomous, parallax, and scroll-scrubbed motion while retaining meaningful media, captions, and reading order.

Implement only the selected winner in the same React + Vite project. Validate the result, preserve the last valid preview if a later experiment fails, and show one interactive candidate. Do not expose internal directions unless asked.
