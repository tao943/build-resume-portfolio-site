# Implementation Workflow

Read this guide only when entering this phase. All paths are relative to the
Skill root unless explicitly workspace-relative. Resolve `SKILL_ROOT` and the
Python executable as described in `SKILL.md`.

Before starting, read:

- [site-planning-contract.md](site-planning-contract.md)
- [react-vite-output-contract.md](react-vite-output-contract.md)
- [structure-seed-contract.md](structure-seed-contract.md)
- [visual-fingerprint-contract.md](visual-fingerprint-contract.md)
- [design-intelligence-contract.md](design-intelligence-contract.md)
- [creative-direction-contract.md](creative-direction-contract.md)
- [design-contract.md](design-contract.md)

## TODO and implementation-plan gate

Use [site-planning-contract.md](site-planning-contract.md) and
[interaction-modes.md](interaction-modes.md). Validate `planning` resources.
Quick mode consumes the approved design/TODO bundle and chooses the execution
arrangement under its delegation. Deep mode consumes explicit requirements,
TODO, and strategy approval, reusing authorization for an unchanged plan.

Write schema-version-2 `.resume-site-work/reports/site-implementation-plan.json`
with `generation_mode: one-integrated-site`, current `interaction_mode`,
strategy evidence, exact tasks, dependencies, files, interfaces, verification,
rollback, and `versions/v1-integrated`. Parallel execution also requires a
validated disjoint `multi-agent-implementation.json`.

```sh
"$PYTHON" "$SKILL_ROOT/scripts/validate_site_implementation_plan.py" \
  ".resume-site-work/reports/site-implementation-plan.json" \
  --design-spec ".resume-site-work/reports/site-design-spec.json" \
  --workspace-root "."
```

Do not edit React source until the design and plan validate. Quick validation
binds the current selection IDs and exact TODO content to the user's approval;
changed choices or tasks need a revised bundle. Preserve facts and copy approval
separately. The main agent owns shared files, integration, state, preview
promotion, snapshots, and publication authorization.

## Generate one integrated website

1. Validate `integrated` resources and set `stage=design_contract_compiling`.
2. Read `prompts/01-generate-integrated-site.md`.
3. Reuse the discovery-stage `reports/content-map.json`, validated database and
   anti-template baselines, five approved category reports, and site design
   spec. Generate the private structural directions before React generation:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/portfolio_design_search.py" recommend \
  --input ".resume-site-work/reports/content-map.json" \
  --baseline ".resume-site-work/reports/design-discovery/baseline.json" \
  --anti-template-baseline ".resume-site-work/reports/design-discovery/anti-template-baseline.json" \
  --site-design-spec ".resume-site-work/reports/site-design-spec.json" \
  --generation-id "<stable-generation-id>" \
  --history ".resume-site-work/history/visual-fingerprints.json" \
  --output ".resume-site-work/reports/design-intelligence.json"
```

   Omit `--history` when it does not exist. Privately compare complete `fit`,
   `novelty`, and `wildcard` directions. Treat
   `script_recommended_direction_id` as evidence, not the final Agent choice;
   the Agent records the final direction, rejected reasons, blocking floors,
   selected topology, variation choices, novelty brief, and a resolution for
   every provisional anti-template rule in schema-version-2
   `reports/creative-direction.json`. Validate it with
   `--design-intelligence`. Do not expose the internal candidates as a new user gate or
   implement losing directions. The choice cannot contradict the five approved
   visual categories.
4. Compile the approved design specification, design intelligence, and creative
   direction into a temporary sibling for `reports/design-contract.json`. Follow
   `references/design-contract.md`, validate the temporary report, and atomically
   replace the canonical report only on success:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/validate_design_contract.py" \
  ".resume-site-work/reports/design-contract.json"
```

   Do not perform the first React source edit before this command exits `0`.
   The contract refines approved choices into observable commitments but cannot
   reopen or contradict them. On failure set `artifact_invalid`, preserve the
   last valid preview and snapshot, and stop source generation.
5. Set `stage=integrated_generating`. Translate the approved decisions and delegated structure and
   validated design contract into implementation detail without changing them.
   Create supporting media-direction, creative-direction, and motion reports
   when applicable.
6. Create or replace the complete source at `.resume-site-work/site` in one
   integrated transaction. Apply structure, typography, color, media treatment,
   one primary-motion system, and all selected compatible secondary effects.
   Create the explicit empty or populated `reports/media-inventory.json`, pass
   it with `--media-inventory` when media validation applies, and follow
   `references/motion-production-contract.md`. Motion has no numeric effect cap;
   compatibility and controller ownership are the limits.
7. Validate and build:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/validate_vite_project.py" \
  ".resume-site-work/site" --stage integrated
(cd ".resume-site-work/site" && npm run build)
```

8. On success, atomically promote `site/dist` to `preview/dist`, capture desktop,
   tablet, mobile, and `interaction_states_checked` evidence for initial and
   representative active states. Inspect coarse-pointer/touch, reduced-motion,
   loading, error, and Poster fallback behavior plus console/layout/media safety.
9. Follow `references/screenshot-review-rules.md` and
   `prompts/04-audit-screenshot.md`. Validate `reports/visual-audit.json` against
   the design contract before repair. Identity fit and aesthetic quality pass
   independently; neither can compensate for failure of the other.
10. Perform evidence-linked bounded local repair with
   `prompts/05-repair-local-issues.md` while `visual_repair_round < 2`. Change
   only finding-level `permitted_files` and the smallest affected region. Do not request
   routine confirmation or silently change a confirmed design decision.
   Keep the last valid preview on failure.
11. Snapshot successful source to `versions/v1-integrated` or a retry suffix,
   set `stage=integrated_waiting_confirmation`, and show the complete website.

The first React candidate is one integrated website. Do not return to the old
prototype, media-direction, and motion confirmation chain.
