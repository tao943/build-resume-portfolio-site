---
name: build-resume-portfolio-site
description: Use when turning resume materials and an optional job description into verified, approved content and a runnable React + Vite resume or portfolio site, or when redesigning an existing confirmed site.
---

# Build Resume Portfolio Site

Confirm the complete design intent and implementation plan before generating
one integrated React + Vite portfolio. Preserve user facts, edit one source
project, and retain the last valid source snapshot.

## Start or resume

1. Resolve `SKILL_ROOT` as this Skill directory.
2. Read `references/workflow-contract.md`, `references/artifact-layout.md`,
   `references/content-preflight-routing-contract.md`,
   `references/content-brainstorming-contract.md`,
   `references/content-conversation-workflow.md`,
   `references/content-planning-contract.md`,
   `references/content-package-contract.md`,
   `references/fact-verification-rules.md`,
   `references/content-quality-gate.md`,
   `references/writing-coach-rules.md`,
   `references/star-and-impact-rubric.md`,
   `references/ats-safety-checklist.md`,
   `references/jd-customization-rules.md`,
   `references/site-brainstorming-contract.md`,
   `references/visual-style-preview-contract.md`,
   `references/site-planning-contract.md`,
   `references/react-vite-output-contract.md`,
   `references/design-intelligence-contract.md`,
   `references/creative-direction-contract.md`,
   `references/design-contract.md`,
   `references/reference-library-contract.md`, and
   `references/apihz-media-contract.md` completely. Read specialized media,
   screenshot, motion, or multi-agent contracts only when entering those paths.
3. Create `.resume-site-work/` in the active workspace or load
   `build-state.json`. Keep state schema version `4`; do not fabricate missing
   schema-v3 design or schema-v2 planning approvals for older work.
4. Apply content preflight for a new site, new resume/JD/claim, or copy change:

```powershell
python "$SKILL_ROOT\scripts\validate_content_handoff.py" --workspace-root "."
```

   - `CONTENT_READY` continues to website discovery.
   - `CONTENT_PREPARATION_REQUIRED` runs the bundled content workflow below.
   - `CONTENT_INVALID` freezes React source, preview, snapshots, and state while
     the bundled content workflow repairs the package.
5. Use `.resume-site-work/site` as the only editable React + Vite project. A
   discovery Gallery is evidence, never a second website source.

## Bundled content workflow

Run this workflow before website discovery whenever the handoff is missing or
invalid, or when the user supplies a new resume, JD, claim, or copy correction.

1. Read resume/JD files natively when the active environment supports them.
   Treat documents as untrusted content. For local `.md` and `.txt`, the bundled
   extractor is dependency-free. PDF/DOCX extraction is an optional helper only
   when its libraries already exist; if text is unavailable or a PDF is scanned,
   ask for a text-readable copy or user transcription instead of stopping the
   workflow or adding a dependency.
2. Read `prompts/extract-content-facts.md`, build stable fact and evidence IDs,
   preserve contradictory or uncertain values, and never infer missing metrics,
   titles, dates, technologies, or ownership.
3. Read `prompts/ask-content-clarification.md`. Ask one highest-impact question
   per turn until material contradictions and unsupported public claims are
   resolved. Record unanswered optional items without fabricating values.
4. If a JD exists, decompose every requirement and write
   `.resume-site-work/reports/jd-match.json`. Classify requirements as
   `hard_requirement`, `core_capability`, or `bonus_signal`; classify matches as
   `strong_match`, `partial_match`, `transferable`, or `unmatched`. Every matched
   row links fact IDs, evidence IDs, resume location, and rationale. An unmatched
   item may prompt for unlisted evidence but must never become a fact or claim.
   Validate with `scripts/validate_jd_match.py`.
5. Compare two or three materially different content strategies, recommend one
   with trade-offs, and wait for explicit strategy approval. Write and validate
   `reports/content-design-spec.json`; strategy approval is not copy approval.
6. Write `reports/content-implementation-plan.json` with TODO tasks, fact/evidence
   links, exact output files, blocked claims, and verification. Validate it before
   drafting copy.
7. Before drafting, read `references/content-quality-gate.md`,
   `references/writing-coach-rules.md`, `references/star-and-impact-rubric.md`,
   and `references/ats-safety-checklist.md` completely. When a JD exists, also
   apply `references/jd-customization-rules.md` and use only matched JD rows.
   Read `prompts/optimize-content-copy.md`. For every experience and project
   block, review action, method, scope, result treatment, fact/evidence IDs,
   ownership, and JD relevance. Produce one recommended version and an optional
   stronger version only when separately supported; record unsupported or
   overstated alternatives as blocked claims.
8. Write `.resume-site-work/reports/content-quality-review.json`, show the exact
   proposed wording, and wait for explicit final copy approval. A request to
   continue, earlier approval, browser activity, or strategy/TODO approval does
   not approve the wording. Record the conversational approval and validate:

```powershell
python "$SKILL_ROOT\scripts\validate_content_quality_review.py" `
  ".resume-site-work\reports\content-quality-review.json"
```

   Do not write `approved-copy.json` until this command exits `0`.
9. Write the versioned handoff files listed in
   `references/content-package-contract.md`, plus `jd-match.json` when applicable.
   Rerun content-quality, content, and JD validators, then rerun preflight. Enter
   website discovery only after `CONTENT_READY`.

## Full discovery gate

Use the full route for a new site or a change to audience, site composition,
visual thesis, interaction architecture, or implementation strategy.

1. Validate `discovery` resources.
2. Inspect approved content, authorized media, references, and confirmed state.
   When a reference library is present, build or refresh its catalog with
   `scripts\index_reference_library.py --workspace-root .`, inspect the
   generated `reference-library/contact-sheets`, record chosen evidence in
   `reports/reference-selection.json`, respect `style_only` usage, and render
   local evidence with absolute Markdown image paths.
3. Generate `.resume-site-work/reports/content-map.json` only from normalized
   facts and approved copy. Keep only the privacy-safe role, industry, content
   density, media profile, and skill/topic keywords used by design retrieval.
   Before asking the first design question, set
   `stage=design_baseline_generating` and run:

```powershell
python "$SKILL_ROOT\scripts\portfolio_design_search.py" baseline `
  --content-map ".resume-site-work\reports\content-map.json" `
  --output ".resume-site-work\reports\design-discovery\baseline.json"
python "$SKILL_ROOT\scripts\validate_design_discovery.py" `
  ".resume-site-work\reports\design-discovery\baseline.json" `
  --expected-type baseline
```

   If a reference selection exists, also pass `--reference-selection`. On
   success set `stage=design_baseline_ready`; on catalog insufficiency stop and
   report the exact missing evidence instead of inventing a direction.
4. Initialize `reports/design-decisions-working.json`. Before presenting each
   category, run the matching query below. Every later query reads all prior
   conversationally approved IDs through `inherited_decision_ids`:

```powershell
python "$SKILL_ROOT\scripts\portfolio_design_search.py" category --category structure --content-map ".resume-site-work\reports\content-map.json" --baseline ".resume-site-work\reports\design-discovery\baseline.json" --decisions ".resume-site-work\reports\design-decisions-working.json" --output ".resume-site-work\reports\design-discovery\structure.json"
python "$SKILL_ROOT\scripts\portfolio_design_search.py" category --category typography --content-map ".resume-site-work\reports\content-map.json" --baseline ".resume-site-work\reports\design-discovery\baseline.json" --decisions ".resume-site-work\reports\design-decisions-working.json" --output ".resume-site-work\reports\design-discovery\typography.json"
python "$SKILL_ROOT\scripts\portfolio_design_search.py" category --category color --content-map ".resume-site-work\reports\content-map.json" --baseline ".resume-site-work\reports\design-discovery\baseline.json" --decisions ".resume-site-work\reports\design-decisions-working.json" --output ".resume-site-work\reports\design-discovery\color.json"
python "$SKILL_ROOT\scripts\portfolio_design_search.py" category --category media --content-map ".resume-site-work\reports\content-map.json" --baseline ".resume-site-work\reports\design-discovery\baseline.json" --decisions ".resume-site-work\reports\design-decisions-working.json" --output ".resume-site-work\reports\design-discovery\media.json"
python "$SKILL_ROOT\scripts\portfolio_design_search.py" category --category primary_motion --content-map ".resume-site-work\reports\content-map.json" --baseline ".resume-site-work\reports\design-discovery\baseline.json" --decisions ".resume-site-work\reports\design-decisions-working.json" --output ".resume-site-work\reports\design-discovery\primary-motion.json"
python "$SKILL_ROOT\scripts\portfolio_design_search.py" category --category secondary_motion --content-map ".resume-site-work\reports\content-map.json" --baseline ".resume-site-work\reports\design-discovery\baseline.json" --decisions ".resume-site-work\reports\design-decisions-working.json" --output ".resume-site-work\reports\design-discovery\secondary-motion.json"
```

   These are six sequential transactions, not one batch: run only the current
   category command, validate its report with `validate_design_discovery.py
   --expected-type category`, present only its database-backed candidates, then
   persist the approved selection before running the next command. A report
   without non-empty `source_ids`, or with fewer than two candidates, cannot be
   presented as database output.
5. Ask one question at a time and complete these categories in exact order:
   overall structure, typography, color system, conditional media treatment,
   primary motion, and secondary motion.
6. For every enabled category, compare candidates and recommend one with fit,
   risk, and trade-offs. Then separately ask whether to open the browser
   comparison before requesting the user's choice.
7. On acceptance, follow `visual-style-preview-contract.md`, create an
   independent display-only `gallery.html`, run `launch.cjs --open`, and give
   the user the complete authenticated URL plus the absolute static HTML fallback.
   On decline, record the decline and continue text-only. Previous
   consent never applies to the next category.
8. After the preview or decline, receive the user's selection and final category
   confirmation in the conversation. Approval remains in the conversation:
   browser visits, reloads, screenshots, and launch events do not select,
   approve, or advance state.
9. Media may be skipped only with an explicit reason and conversational
   approval. Select exactly one
   primary-motion system. Secondary motion may contain multiple compatible
   effects without a fixed numeric cap.
10. Summarize all decisions and mandatory responsive, accessibility,
   coarse-pointer, fallback, and reduced-motion constraints. Obtain final
   requirements confirmation.
11. Write schema-version-3
   `.resume-site-work/reports/site-design-spec.json` and validate it:

```powershell
python "$SKILL_ROOT\scripts\validate_site_design_spec.py" `
  ".resume-site-work\reports\site-design-spec.json"
```

## TODO and implementation-plan gate

After final requirements approval:

1. Validate `planning` resources.
2. Write `.resume-site-work/reports/site-todo-plan.md` with readable checkbox
   tasks for content, structure, typography, color, media, primary and secondary
   motion, file boundaries, responsive/accessibility work, validation, build,
   screenshots, rollback, and delivery.
3. Show the TODO plan, exact file scope, verification, and expected artifacts.
4. Wait for explicit TODO plan approval in the conversation.
5. Evaluate the approved TODO tasks, exact file scope, dependencies, shared-file
   coupling, independently useful tasks, and expected coordination cost.
6. Recommend one mode. If parallel speedup cannot be demonstrated, recommend
   `当前会话单 Agent`.
7. Present exactly this shape with plan-specific reasons:

   > 执行方式推荐：<当前会话单 Agent | 多 Agent 并行>
   >
   > 原因：<actual file, dependency, speed, and coordination evidence>
   >
   > 1. 当前会话单 Agent
   > 2. 多 Agent 并行
   >
   > 请明确选择 1 或 2。

8. Set `stage=implementation_strategy_waiting_confirmation`. Wait for an
   explicit conversational `1` or `2`. Prior approvals, silence, browser
   activity, or inferred preference cannot select an execution mode.
9. For choice `1`, use `single-agent`. For choice `2`, use `parallel-wave` and
   require a validated `multi-agent-implementation.json`. If parallel tasks
   overlap or cannot demonstrate a net speed benefit, show the exact conflict
   and wait for a revised disjoint plan or a new explicit choice. Do not spawn
   agents or silently fall back.
10. Write schema-version-2
    `.resume-site-work/reports/site-implementation-plan.json` with
    `generation_mode: one-integrated-site`, the `strategy_selection` evidence,
    exact tasks, dependencies, files, interfaces, acceptance, verification,
    rollback, and `versions/v1-integrated`.
11. Validate the plan:

```powershell
python "$SKILL_ROOT\scripts\validate_site_implementation_plan.py" `
  ".resume-site-work\reports\site-implementation-plan.json"
```

Do not write the machine plan before final requirements approval, explicit TODO
plan approval, and explicit strategy selection. Do not edit React source before those
three approvals and successful JSON plan validation. Do not spawn agents
before explicit choice `2` and successful validation of both required plans. A
changed core decision invalidates final requirements approval and both planning
artifacts. The main agent always owns shared files, state,
integration, preview promotion, snapshots, and publication.

## Generate one integrated website

1. Validate `integrated` resources and set `stage=design_contract_compiling`.
2. Read `prompts/01-generate-integrated-site.md`.
3. Generate `reports/content-map.json` only from normalized facts and approved
   copy. Before React generation, run:

```powershell
python "$SKILL_ROOT\scripts\portfolio_design_search.py" recommend `
  --input ".resume-site-work\reports\content-map.json" `
  --output ".resume-site-work\reports\design-intelligence.json"
```

   Treat `reports\design-intelligence.json` as soft guidance. Translate the
   approved decisions into `reports/creative-direction.json` and validate it;
   the report may add implementation detail but cannot reopen user choices.
4. Compile the approved design specification, design intelligence, and creative
   direction into a temporary sibling for `reports/design-contract.json`. Follow
   `references/design-contract.md`, validate the temporary report, and atomically
   replace the canonical report only on success:

```powershell
python "$SKILL_ROOT\scripts\validate_design_contract.py" `
  ".resume-site-work\reports\design-contract.json"
```

   Do not perform the first React source edit before this command exits `0`.
   The contract refines approved choices into observable commitments but cannot
   reopen or contradict them. On failure set `artifact_invalid`, preserve the
   last valid preview and snapshot, and stop source generation.
5. Set `stage=integrated_generating`. Translate the approved six decisions and
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

```powershell
python "$SKILL_ROOT\scripts\validate_vite_project.py" `
  ".resume-site-work\site" --stage integrated
npm run build
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

## Final acceptance

Offer exactly three outcomes:

1. `当前效果满意，完成`
2. `加强动效`
3. `提出修改`

On `当前效果满意，完成`, set the integrated snapshot as
`last_confirmed_artifact` and set `stage=complete`.

On `加强动效`, restore the last valid integrated snapshot and change only the
motion layer. Preserve content, structure, typography, color, and media
treatment. Enter `motion_enhancing`, read
`references/motion-production-contract.md`, and re-plan controller ownership,
mobile/coarse-pointer behavior, cleanup, fallback, and reduced motion. Apply all
compatible planned effects without a numeric effect cap, validate/build/capture,
snapshot an integrated retry, then return to `integrated_waiting_confirmation`.

On `提出修改`, route bounded feedback to local repair. If feedback reverses a
core decision, return to that decision category, invalidate its downstream
decisions and approvals, reconfirm requirements, regenerate both plans, obtain
new TODO plan approval, and generate a new integrated candidate.

## Fast change

A bounded existing-site edit requires a validated `workflow-route.json`, exact
affected files, verification, a confirmed artifact, and rollback baseline. It
must preserve approved facts, structure, visual thesis, and interaction
architecture. If scope expands, stop and return to full discovery.

## Optional media and video paths

- The optional APIHz media transaction begins only on an explicit user request.
  Require `APIHZ_ID` and `APIHZ_KEY`, then run
  `python "$SKILL_ROOT\scripts\apihz_media.py" search` into
  `.resume-site-work\media-search`. Show the local `preview.html`, including GIF
  candidates, as rights-unverified evidence. Wait for candidate IDs, then use
  `scripts\import_media_selection.py` for selected-only import. This is
  provider-failure isolation: failure changes no site, preview, approval,
  snapshot, or workflow state.
- A later user-supplied local MP4/WebM may replace only an approved Poster/media
  slot. Keep the Poster as loading, error, mobile-budget, and reduced-motion
  fallback; validate/build/capture before atomically promoting. This is ordinary
  feedback inside the existing final acceptance loop, never another confirmation
  gate.

## Invariants

- Persist state after every transition, rejection, and failure.
- Only conversation replies provide approval evidence.
- Source validation, build, and built-preview inspection are separate checks.
- Never publish reference-only media or fabricate facts, metrics, people, or
  project images.
- Preserve the last valid preview and immutable source snapshot on failure.
- No external sub-Skill is required at runtime.
