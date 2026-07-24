---
resource_id: add-motion
resource_version: 1
resource_status: ready
output_contract: react-vite-project-update-and-motion-plan-json
---

# Production-harden the confirmed motion layer

Production-harden purposeful motion in the same React + Vite project that already passed styling and screenshot review. Consume the confirmed media direction/report/refined audit and installed effect sources; preserve their visual thesis, confirmed resume facts, page regions, visual hierarchy, palette, typography, layout, responsive behavior, and content order. This is not a redesign.

## Required inputs

- `.resume-site-work/site/`
- `.resume-site-work/reports/style-brief.json`
- `.resume-site-work/reports/visual-audit.json`
- `references/motion-safety-rules.md`
- `references/motion-production-contract.md`

Stop with `resource_blocked` when the refined project or required confirmed reports are absent. Use only sources the direction needs: CSS/native, React Bits, MotionSite, Motion, GSAP, or Three.js are all conditional options. React Bits is not mandatory.

## Procedure

1. Inventory confirmed effects/controllers and their installed effect sources. Merge compatible controller ownership into shared timelines; isolate a section if a conflict cannot be shared safely. There is no numeric effect cap.
2. If React Bits is selected, run `scripts/ensure_react_bits_registry.py` and use exact `@react-bits` registry variants through the shadcn MCP. Otherwise use only the installed source needed by the direction.
3. Write `.resume-site-work/reports/motion-plan.json` before editing source. Every item needs a unique ID plus source, target, purpose, controllers, dependencies, conflict_resolution, cleanup, mobile, reduced_motion, and fallback.
4. Integrate only the planned effects and required dependencies in the same React + Vite project. Keep content immediately accessible; do not add scroll hijacking, cursor replacement, autoplay audio, blocking loaders, or a second visual redesign.
5. Add lifecycle cleanup, component-level fallbacks, a CSS `@media (prefers-reduced-motion: reduce)` rule, and static reduced-motion equivalents. Disable or simplify continuous effects on mobile/coarse pointers when needed.
6. Run `validate_vite_project.py` with `--stage motion`, then run `npm run build`. Inspect desktop, tablet, mobile/coarse-pointer, and reduced-motion captures for layout movement, clipping, console errors, and performance regressions. Preserve Poster/media safety and snapshot `.resume-site-work\\versions\\v4-motion`.

## Output

Return only:

1. the updated source in `.resume-site-work/site/`;
2. the schema-conformant `reports/motion-plan.json`;
3. a concise inventory of installed effect sources, controllers, and dependencies;
4. verification results for source validation, `npm run build`, responsive captures, and reduced motion.

Do not create standalone HTML, a second Vite project, or an untracked demo page.
