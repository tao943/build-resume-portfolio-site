# Motion Production Contract

Stage 4 productionizes motion already justified by the confirmed media direction/report/refined audit. It preserves that visual thesis, the confirmed baseline, factual content, responsive hierarchy, and Poster/media safety; it does not trigger a redesign.

## Source selection and hardening

- Inventory the confirmed effects, controllers, dependencies, and installed effect sources before editing. Sources may include CSS/native, React Bits, MotionSite, Motion, GSAP, and Three.js; select only what the direction needs. React Bits is conditional, not mandatory.
- There is **no numeric effect cap**. Prefer compatible effects that share a timeline/controller; isolate a section when shared ownership would create a conflict.
- Add lifecycle cleanup for every controller, a coarse-pointer/mobile alternative, a static reduced-motion equivalent, and a resilient fallback. Keep source code and dependencies in the same React + Vite project.
- Do not introduce scroll hijacking, cursor replacement, autoplay audio, blocking loaders, delayed content access, or remote runtime dependencies.

## Required motion plan

Write `reports/motion-plan.json` before source edits. Each item has a unique `id` and declares `source`, `target`, `purpose`, `controllers`, `dependencies`, `conflict_resolution`, `cleanup`, `mobile`, `reduced_motion`, and `fallback`. The plan records shared timelines or explicitly explains an isolated/conflicting controller.

## Verification and snapshot

Validate the motion source, build it, and inspect desktop, tablet, mobile/coarse-pointer, and reduced-motion states. Confirm the Poster/media fallback remains safe. On success snapshot `.resume-site-work\\versions\\v4-motion` (or a retry suffix); that snapshot is the confirmed baseline for optional MotionSite enhancement.
