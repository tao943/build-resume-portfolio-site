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
- `reports/site-design-spec.json` schema version 3;
- `reports/site-todo-plan.md` as the user-approved readable plan;
- `reports/site-implementation-plan.json` schema version 2;
- `reports/design-intelligence.json` as soft design guidance;
- `reports/media-inventory.json` when authorized media exists.

Do not implement when final requirements or TODO plan approval is missing.

## Integrated implementation

Apply all confirmed decisions in the same source transaction:

- overall structure and content hierarchy;
- typography roles, scale, rhythm, and reading texture;
- color tokens, contrast, and semantic roles;
- confirmed media treatment and local fallbacks, or the approved no-media path;
- exactly one primary-motion system;
- every selected compatible secondary effect.

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

Generate the complete source plus `reports/content-map.json`, motion planning
evidence, and media-direction evidence when media is enabled. Then run the Skill
project validator with `--stage integrated`, `npm run build`, and responsive
screenshot capture. Repair only bounded observable defects, at most twice,
without changing confirmed design decisions. Promote and snapshot only a
successful integrated build.
