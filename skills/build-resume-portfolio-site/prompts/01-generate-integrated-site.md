---
resource_id: generate-integrated-site
resource_version: 1
resource_status: ready
output_contract: react-vite-integrated-site
---

# Generate the integrated portfolio site

Create one complete React + Vite portfolio at `.resume-site-work/site`. This is
the first user-facing website candidate, not a structural prototype.

## Required inputs

Read and preserve:

- `input/normalized-resume.json` as factual evidence;
- `input/approved-copy.json` as visible-copy authority;
- `reports/site-design-spec.json` schema version 4 for new full workflows, or
  an unmigrated schema-version-3 report under its original approved semantics;
- `reports/site-todo-plan.md` as the user-approved readable plan;
- `reports/site-implementation-plan.json` schema version 2;
- `reports/design-intelligence.json` schema version 2 with private fit,
  novelty, and wildcard directions, the database/anti-template baselines, and a
  script recommendation;
- validated `reports/creative-direction.json` schema version 2 containing the
  Agent's final selection and semantic rationale;
- validated `reports/design-contract.json` as observable implementation and
  acceptance commitments;
- `reports/media-inventory.json` when authorized media exists.

Do not implement when final requirements or TODO plan approval is missing.
Resolve every provisional anti-template rule through approved evidence while
selecting structure; do not reinterpret the five user-approved visual categories.

## Integrated implementation

Apply all confirmed/delegated decisions in the same source transaction. Do not
implement the two losing internal directions:

- overall structure and content hierarchy;
- typography roles, scale, rhythm, and reading texture;
- color tokens, contrast, and semantic roles;
- confirmed media treatment and local fallbacks, or the approved no-media path;
- exactly one signature motion family, planned only after the static
  composition is selected;
- every selected compatible secondary effect.

Implement every applicable `design-contract.json` commitment. Preserve its
identity strategy and signature device; apply its layout, typography, color,
surface, primary-motion, compatible-secondary-motion, responsive, and fallback
rules. Treat `anti_template_rules` and `acceptance_checks` as observable output
criteria, not optional inspiration. Content fit does not establish aesthetic
quality, and decorative polish does not establish identity fit.

The structural seed fixes only topology, reading mechanics, invariants,
responsive transformation, anti-degeneracy rules, and compatible motion slots.
Choose color, type, component expression, media treatment, visual protagonist,
surface language, and concrete motion for this generation. Three.js is allowed
only when it is the protagonist or narrative medium and passes every gate in
`motion-production-contract.md`; never add it as generic background particles.

Keep resume content in a centralized data module. Use semantic sections for
hero, experience, projects, strengths, and contact, but let the confirmed
structure determine their composition rather than applying a generic template.
Target an expressive desktop composition around 1700px while remaining usable
at tablet and 390px mobile widths without horizontal overflow.

## Engineering requirements

- Use local, authorized media only; never fabricate factual project images.
- Provide loading/error/static fallbacks for media and motion.
- Provide visible focus, keyboard navigation, sufficient contrast, semantic
  headings, and meaningful alternative text.
- Resolve controller ownership across primary and secondary effects.
- Provide coarse-pointer/mobile alternatives and a complete
  `prefers-reduced-motion: reduce` presentation.
- Clean up observers, listeners, animation frames, timelines, and WebGL state.
- Keep `package.json` scripts for `dev` and `build`; do not switch frameworks,
  use CDN React, or create a second standalone HTML site.

## Output and verification

Generate the complete source plus `reports/content-map.json`, validated
`reports/design-contract.json`, motion planning
evidence, and media-direction evidence when media is enabled. Then run the Skill
project validator with `--stage integrated`, `npm run build`, and responsive
screenshot capture. Repair only bounded observable defects, at most twice,
without changing confirmed design decisions. Promote and snapshot only a
successful integrated build.
