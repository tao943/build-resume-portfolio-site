# Creative Direction Contract

## Purpose

`creative-direction.json` preserves the approved creative intent from
brainstorming through implementation and review. It defines a fixed floor and
an open ceiling:

- the fixed floor protects facts, priorities, mandatory content and media,
  approved interactions, accessibility, fallback behavior, and explicit
  prohibitions;
- the open ceiling keeps composition, creative layout, motion language, visual
  metaphor, texture, and surface treatment available for exploration.

It is not a template, source-code payload, or component tree.
It is not a new workflow stage or confirmation gate.

## Creation

Create the report after `design-intelligence.json` and before the first React
source edit. Use the user's approved direction and normalized facts. Compare
two or three materially different layout families before selecting one.
Candidate vocabulary may include Kinetic Marquee, Horizontal Pan, Coverflow
Carousel, Drag-to-Pan Grid, Sticky Stack, Split-Screen Scroll, Hover Image
Trail, and Parallax Tilt Card, but the vocabulary is a search space rather than
a required menu.

Write `.resume-site-work/reports/creative-direction.json` and validate it:

```powershell
python "$SKILL_ROOT\scripts\validate_creative_direction.py" `
  ".resume-site-work\reports\creative-direction.json"
```

Continue only on exit `0`.

## Required decisions

- `creative_thesis`: one emotional and visual proposition.
- `experience_priority`: ordered attention and narrative goals.
- `creative_freedom.fixed`: user-approved invariants.
- `creative_freedom.open`: separate exploration spaces for composition,
  layout patterns, motion language, visual metaphor, and surface treatment.
- `creative_freedom.avoid`: rejected patterns and failure modes.
- `layout_candidates`: two or three distinct families with fit, risk, and
  responsive fallback.
- `selected_candidate_id` and `selection_rationale`.
- `concept_prototype`: the first-version visual commitments.
- responsive and motion freedoms.
- observable `review_questions`.

Fixed, open, and avoid entries must not overlap. Open entries describe intent
and possibility, not pixel dimensions, exact grids, JSX, HTML, class names, or
component trees.

## Visual concept prototype

Stage 1 is a visual concept prototype, not a neutral wireframe. Before source
work, `concept_prototype` must commit to:

- `visual_protagonist`: one dominant subject or visual anchor;
- `composition_commitment`: a visible expression of the selected layout
  family;
- `type_color_character`: an initial typography and color personality;
- `representative_interaction_state`: one static or lightweight active state
  that proves the interaction idea;
- `template_independence_test`: why the page remains recognizable without
  final media or motion;
- `deferred_to_later`: reference-derived finishing, final media treatment, and
  production motion only.

Initial hierarchy, the selected layout family, type/color character, and the
representative interaction cannot be deferred. Media finishing and complex
motion remains deferred to their existing stages.

## Evolution

Media direction may enrich open choices using approved references and assets.
It must not silently change the fixed floor or remove avoid rules. User
feedback may revise the contract; record the revision before editing source.
A rejected prototype may select another unused candidate while preserving the
same fixed floor unless the user explicitly changes it.

Every implementation task packet receives the creative thesis, relevant fixed
items, relevant open spaces, avoid rules, and review questions. Reviewers test
whether implementation expresses the selected direction without collapsing
the open ceiling into a generic template.
