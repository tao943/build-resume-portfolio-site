# Structure seed contract

`assets/structure-seeds/catalog.json` is a versioned library of high-impact
reading topologies. A seed is not a template: it may define reading path,
relationships, capacity, invariants, variation axes, responsive transformations,
anti-degeneracy rules, cost, and optional motion slots only. It must not contain
fixed JSX/HTML, palettes, fonts, named components, assets, shaders, durations, or
easing values.

New full workflows filter seeds using privacy-safe counts, media classes, and
delivery constraints. Structure is universal and must not be chosen from job
title, industry, personal details, or resume keywords. Generate two distinct
seed candidates (`fit` and `novelty`) and one constrained `wildcard`. A wildcard
uses the same five-field canonical topology signature as seeds and must have
weighted distance at least `0.35` from every seed.

The catalog exposes optional motion slots; concrete motion is compiled only
after the Agent selects a complete composition. Three.js is never required by a
seed. Validate the catalog before recommendation with
`scripts/validate_structure_seeds.py`.
