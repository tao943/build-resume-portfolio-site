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
   category, run the matching query below. Every later query reads all prior
   conversationally approved IDs through `inherited_decision_ids`, and every
   query evaluates candidates against the same anti-template baseline:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" category --category typography --content-map ".resume-site-work/reports/content-map.json" --baseline ".resume-site-work/reports/design-discovery/baseline.json" --anti-template-baseline ".resume-site-work/reports/design-discovery/anti-template-baseline.json" --decisions ".resume-site-work/reports/design-decisions-working.json" --output ".resume-site-work/reports/design-discovery/typography.json"
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" category --category color --content-map ".resume-site-work/reports/content-map.json" --baseline ".resume-site-work/reports/design-discovery/baseline.json" --anti-template-baseline ".resume-site-work/reports/design-discovery/anti-template-baseline.json" --decisions ".resume-site-work/reports/design-decisions-working.json" --output ".resume-site-work/reports/design-discovery/color.json"
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" category --category media --content-map ".resume-site-work/reports/content-map.json" --baseline ".resume-site-work/reports/design-discovery/baseline.json" --anti-template-baseline ".resume-site-work/reports/design-discovery/anti-template-baseline.json" --decisions ".resume-site-work/reports/design-decisions-working.json" --output ".resume-site-work/reports/design-discovery/media.json"
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" category --category primary_motion --content-map ".resume-site-work/reports/content-map.json" --baseline ".resume-site-work/reports/design-discovery/baseline.json" --anti-template-baseline ".resume-site-work/reports/design-discovery/anti-template-baseline.json" --decisions ".resume-site-work/reports/design-decisions-working.json" --output ".resume-site-work/reports/design-discovery/primary-motion.json"
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" category --category secondary_motion --content-map ".resume-site-work/reports/content-map.json" --baseline ".resume-site-work/reports/design-discovery/baseline.json" --anti-template-baseline ".resume-site-work/reports/design-discovery/anti-template-baseline.json" --decisions ".resume-site-work/reports/design-decisions-working.json" --output ".resume-site-work/reports/design-discovery/secondary-motion.json"
```

   These are five sequential transactions, not one batch: run only the current
   category command, validate its report with `validate_design_discovery.py
   --expected-type category`, present only its database-backed candidates, then
   persist the approved selection before running the next command. A report
   without non-empty `source_ids`, or with fewer than two candidates, cannot be
   presented as database output.
6. Record structure as Agent-delegated with `visual-impact` priority, universal
   scope, `fit-novelty-wildcard` exploration, and direct generation. Do not ask
   the user to choose a seed. Ask one question at a time for typography, color
   system, conditional media treatment, primary motion, and secondary motion.
7. For every enabled category, compare candidates and recommend one with fit,
   risk, and trade-offs. Then separately ask whether to open the browser
   comparison before requesting the user's choice.
8. On acceptance, follow `visual-style-preview-contract.md`, create an
   independent display-only `gallery.html`, run `launch.cjs --open`, and give
   the user the complete authenticated URL plus the absolute static HTML fallback.
   On decline, record the decline and continue text-only. Previous
   consent never applies to the next category.
9. After the preview or decline, receive the user's selection and final category
   confirmation in the conversation. Approval remains in the conversation:
   browser visits, reloads, screenshots, and launch events do not select,
   approve, or advance state.
10. Media may be skipped only with an explicit reason and conversational
   approval. Select exactly one
   primary-motion system. Secondary motion may contain multiple compatible
   effects without a fixed numeric cap.
11. Summarize all decisions and mandatory responsive, accessibility,
   coarse-pointer, fallback, and reduced-motion constraints. Obtain final
   requirements confirmation.
12. Write schema-version-4
   `.resume-site-work/reports/site-design-spec.json` and validate it:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/validate_site_design_spec.py" \
  ".resume-site-work/reports/site-design-spec.json"
```

