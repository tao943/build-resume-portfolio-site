# Structure seed QA fixture

This React + Vite fixture exercises three structurally distant, high-risk seeds:
`split-narrative`, `pinned-chapter-stage`, and `constellation-map`. It uses
generic evidence and intentionally neutral tokens so it validates topology, not
a reusable visual template.

Build from the repository root with:

```powershell
node ../../frontend/node_modules/vite/bin/vite.js build skills/build-resume-portfolio-site/tests/structure-seed-fixtures
```

Use `?seed=<id>` to capture each structure. Verify desktop, 390px mobile, and
reduced-motion modes. Core evidence must remain visible with JavaScript motion
disabled.
