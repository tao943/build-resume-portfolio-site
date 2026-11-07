# Discovery Workflow

Read this guide only when entering this phase. All paths are relative to the
Skill root unless explicitly workspace-relative. Resolve `SKILL_ROOT` and the
Python executable as described in `SKILL.md`.

Before starting, read:

- [site-brainstorming-contract.md](site-brainstorming-contract.md)
- [visual-style-preview-contract.md](visual-style-preview-contract.md)
- [structure-seed-contract.md](structure-seed-contract.md)
- [visual-fingerprint-contract.md](visual-fingerprint-contract.md)
- [design-intelligence-contract.md](design-intelligence-contract.md)

Read [interaction-modes.md](interaction-modes.md) and persist the current
`interaction_mode` before discovery.

## Full discovery gate

Use the full route for a new site or a change to audience, overall structure,
visual thesis, interaction architecture, or implementation strategy.

1. Validate `discovery` resources.
2. Inspect approved content, authorized media, references, and confirmed state.
   When a reference library is present, build or refresh its catalog with
   `scripts/index_reference_library.py --workspace-root .`, inspect the
   generated `reference-library/contact-sheets`, record chosen evidence in
   `reports/reference-selection.json`, respect `style_only` usage, and render
   local evidence with absolute Markdown image paths.
3. Generate `.resume-site-work/reports/content-map.json` only from normalized
   facts and approved copy. Keep only the privacy-safe role, industry, content
   density, media profile, and skill/topic keywords used by design retrieval.
   Before asking the first design question, set
   `stage=design_baseline_generating` and run:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" baseline \
  --content-map ".resume-site-work/reports/content-map.json" \
  --output ".resume-site-work/reports/design-discovery/baseline.json"
"$PYTHON" "$SKILL_ROOT/scripts/validate_design_discovery.py" \
  ".resume-site-work/reports/design-discovery/baseline.json" \
  --expected-type baseline
```

   If a reference selection exists, also pass `--reference-selection`. On
   success set `stage=design_baseline_ready`; on catalog insufficiency stop and
   report the exact missing evidence instead of inventing a direction.
4. Before delegating structure, set
   `stage=anti_template_baseline_generating`, compile the database baseline into
   a provisional project-specific visual thesis, and validate it:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" anti-template-baseline \
  --content-map ".resume-site-work/reports/content-map.json" \
  --baseline ".resume-site-work/reports/design-discovery/baseline.json" \
  --output ".resume-site-work/reports/design-discovery/anti-template-baseline.json"
"$PYTHON" "$SKILL_ROOT/scripts/validate_design_discovery.py" \
  ".resume-site-work/reports/design-discovery/anti-template-baseline.json" \
  --expected-type anti_template_baseline
```

   On success set `stage=anti_template_baseline_ready`. This provisional
   artifact does not select any of the six categories or authorize React source
   edits. The provisional baseline is not approval.
   Browser preview and user choice remain approvals for the five user-selected
   categories. Structure selection itself remains an internal Agent decision.
5. Initialize `reports/design-decisions-working.json`. Before presenting each
   category, run the matching query below. Each query reads only previously
   conversationally approved IDs through `inherited_decision_ids`, and every
   query evaluates candidates against the same anti-template baseline:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" category --category typography --content-map ".resume-site-work/reports/content-map.json" --baseline ".resume-site-work/reports/design-discovery/baseline.json" --anti-template-baseline ".resume-site-work/reports/design-discovery/anti-template-baseline.json" --decisions ".resume-site-work/reports/design-decisions-working.json" --output ".resume-site-work/reports/design-discovery/typography.json"
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" category --category color --content-map ".resume-site-work/reports/content-map.json" --baseline ".resume-site-work/reports/design-discovery/baseline.json" --anti-template-baseline ".resume-site-work/reports/design-discovery/anti-template-baseline.json" --decisions ".resume-site-work/reports/design-decisions-working.json" --output ".resume-site-work/reports/design-discovery/color.json"
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" category --category media --content-map ".resume-site-work/reports/content-map.json" --baseline ".resume-site-work/reports/design-discovery/baseline.json" --anti-template-baseline ".resume-site-work/reports/design-discovery/anti-template-baseline.json" --decisions ".resume-site-work/reports/design-decisions-working.json" --output ".resume-site-work/reports/design-discovery/media.json"
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" category --category primary_motion --content-map ".resume-site-work/reports/content-map.json" --baseline ".resume-site-work/reports/design-discovery/baseline.json" --anti-template-baseline ".resume-site-work/reports/design-discovery/anti-template-baseline.json" --decisions ".resume-site-work/reports/design-decisions-working.json" --output ".resume-site-work/reports/design-discovery/primary-motion.json"
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" category --category secondary_motion --content-map ".resume-site-work/reports/content-map.json" --baseline ".resume-site-work/reports/design-discovery/baseline.json" --anti-template-baseline ".resume-site-work/reports/design-discovery/anti-template-baseline.json" --decisions ".resume-site-work/reports/design-decisions-working.json" --output ".resume-site-work/reports/design-discovery/secondary-motion.json"
```

   Validate every report with `validate_design_discovery.py --expected-type
   category`. A report without non-empty `source_ids`, or fewer than two
   candidates, cannot be presented as database output.
6. Record structure as Agent-delegated with `visual-impact` priority, universal
   scope, `fit-novelty-wildcard` exploration, and direct generation. Do not ask
   the user to choose a seed.
7. In deep mode, query, present, and confirm each category before querying the
   next, saving approved IDs in the working decisions file. In quick mode,
   query the five categories against the common baselines and only existing
   approved IDs. Keep all new recommendations tentative until the bundle is
   approved; internally verify compatibility across the combined selections.
8. Follow `visual-style-preview-contract.md`. Reuse authorized preview
   preference and one browser session. Quick mode uses one combined gallery;
   deep mode refreshes that session with the current category. Declined
   previews stay text-only for the user's stated scope.
9. Quick mode presents a combined design and TODO plan with delegated execution;
   record one explicit bundle approval as described in `interaction-modes.md`.
   Deep mode receives conversational category selections and summarizes them
   for final requirements approval. Browser activity never constitutes approval.
10. Media can be skipped with an explicit reason included in that approval.
    Select exactly one primary-motion system and compatible secondary effects.
11. Retain responsive, accessibility, coarse-pointer, fallback, and reduced-motion
    constraints in both modes. A user revision changes only affected choices
    and requires updating the relevant approval, not restarting unrelated work.
12. Write schema-version-4
   `.resume-site-work/reports/site-design-spec.json` and validate it:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/validate_site_design_spec.py" \
  ".resume-site-work/reports/site-design-spec.json"
```
