---
name: build-resume-portfolio-site
description: Create or redesign runnable React + Vite resume and portfolio websites from resume content, portfolio materials, visual references, or screenshots. Use when Codex needs to build a content-driven portfolio prototype, apply a reference-derived visual style, repair local visual defects from responsive screenshots, add restrained motion, or resume this staged workflow.
---

# Build Resume Portfolio Site

Build one directly runnable React + Vite portfolio through four controlled stages. Preserve user facts, edit one source project, and retain the last confirmed source snapshot.

## Start or resume

1. Resolve `SKILL_ROOT` as this Skill directory.
2. Read `references/workflow-contract.md`, `references/artifact-layout.md`, `references/content-preflight-routing-contract.md`, `references/site-brainstorming-contract.md`, `references/site-planning-contract.md`, `references/react-vite-output-contract.md`, `references/reference-library-contract.md`, `references/design-intelligence-contract.md`, `references/creative-direction-contract.md`, and `references/apihz-media-contract.md` completely. When the user explicitly authorizes multi-agent implementation, also read `references/multi-agent-implementation-contract.md` completely before dispatch.
3. Create `.resume-site-work/` in the active user workspace or load `build-state.json`. The active state schema is version `4`. A version-3 state may be migrated only with `scripts/migrate_build_state.py` into a distinct output file; reject every other old schema and never infer a migration.
4. Apply content preflight before a new Stage 1 build, when a new resume/JD/claim is supplied, or when the user requests factual/copy changes. Skip it only to resume an existing confirmed site for visual, media, motion, responsive, accessibility, or frontend-only work.
5. For content preflight, run:

```powershell
python "$SKILL_ROOT\scripts\validate_content_handoff.py" --workspace-root "."
```

   - On `CONTENT_READY` (exit `0`), consume the approved package directly.
   - On `ROUTE_REQUIRED` (exit `2`), **REQUIRED SUB-SKILL:** Use `resume-content-intelligence`. Wait for content approval and handoff, then rerun the validator.
   - On `CONTENT_INVALID` (exit `1`), do not edit source, state, preview, or snapshots. Use the content Skill to repair or revise the package, then rerun validation.
6. Normalize only authorized links and local media that are outside the content package. Do not silently rewrite approved copy, renormalize approved facts, or promote draft/inferred claims.
7. Use `.resume-site-work\site` as the only editable React + Vite project. Do not create a parallel standalone HTML page.
8. Resume the recorded stage. Load only the resources required by that stage.

## Discovery and implementation-plan gate

For a new site or structural, strategic, visual-direction, interaction-family,
or implementation-strategy change:

1. Validate `discovery` resources.
2. Inspect approved content, authorized media, references, and existing state.
3. Ask one question at a time; each question must be decision-bearing.
4. Compare two or three materially different layout or experience families.
5. Write `.resume-site-work\reports\site-design-spec.json`, validate it with
   `scripts\validate_site_design_spec.py`, show the recommendation and
   trade-offs, and wait for explicit user approval.
6. Validate `planning` resources.
7. Write `.resume-site-work\reports\site-implementation-plan.json` with exact
   files, dependencies, interfaces, acceptance, verification, rollback, and
   snapshot target. Validate it with
   `scripts\validate_site_implementation_plan.py`.
8. Select the implementation strategy, then enter Stage 1 or the relevant
   confirmed-stage transaction.

Do not edit React source before the site design specification is explicitly
approved and the site implementation plan validates.

For a bounded existing-site change, require a validated
`reports/workflow-route.json` with route `site-fast-change`, exact affected
files, verification, confirmed artifact, and rollback baseline. Preserve the
approved content, structure, visual thesis, and interaction architecture. If
scope expands, stop edits and return to the full discovery gate.

An explicitly migrated version-3 state with a valid confirmed snapshot may
enter `fast-change-eligible` mode without retroactively inventing discovery or
planning approval. It still uses the fast-change route only when the requested
edit satisfies every bounded-change condition above.

No external Superpowers skill is required at runtime.

## Resource and project checks

Before each stage, run:

```powershell
python "$SKILL_ROOT\scripts\validate_skill_resources.py" --mode runtime --stage <prototype|media-direction|screenshot|motion>
```

Continue only on exit `0`. Exit `2` means approved stage material is unavailable; exit `1` means malformed or missing resources. Report the exact resource and stop instead of substituting a generic prompt, template, or style.

After every source edit, validate `.resume-site-work\site`:

```powershell
python "$SKILL_ROOT\scripts\validate_vite_project.py" ".resume-site-work\site" --stage <prototype|styled|refined|motion>
```

Then run `npm run build` from `.resume-site-work\site`. If dependencies are missing, ask for approval before running `npm install`; do not silently switch to CDN React, standalone HTML, or another framework. Only after validation and build succeed:

- atomically replace `.resume-site-work\preview\dist` with `.resume-site-work\site\dist`;
- set the active preview to `.resume-site-work\preview\dist\index.html`;
- create an immutable source snapshot with `scripts\snapshot_vite_project.py`;
- update `current_artifact` and `current_preview` in state.

Keep the previous valid preview active when validation or build fails. For repeat attempts, add `-r2`, `-r3`, and so on to the snapshot directory rather than overwriting it.

## Select the implementation strategy

Choose the implementation strategy after scope and design intent are approved,
the site implementation plan validates, and before editing source:

- use `single-agent` for local or tightly coupled changes;
- use `fresh-agent-sequential` when fresh contexts help but tasks form a
  dependency chain;
- use `parallel-wave` only for independently useful tasks with disjoint file
  ownership.

Multi-agent execution requires explicit user authorization. It does not add a
workflow stage or confirmation gate. The main agent remains the visual director
and integration owner; do not divide pages merely to maximize agent count.

For either multi-agent strategy, read
`references/multi-agent-implementation-contract.md`, write
`reports/multi-agent-implementation.json`, and validate it before dispatch:

```powershell
python "$SKILL_ROOT\scripts\validate_multi_agent_plan.py" `
  ".resume-site-work\reports\multi-agent-implementation.json"
```

Require bounded task packets, no overlapping file ownership in parallel waves,
shared-file ownership by the integration task, and independent read-only review.
Subagents never promote previews, create snapshots, change workflow state, or
install dependencies. The main agent performs the original stage transaction
once after integration and review.

## Stage 1: Generate the visual concept prototype

1. Validate `prototype` resources.
2. Read `prompts/01-generate-prototype.md` and generate `reports/content-map.json` only from `input/normalized-resume.json` and `input/approved-copy.json`. Use normalized facts as evidence and approved blocks as visible-copy input; do not silently rewrite them or use drafts and low-confidence inference.
3. Before creating React source, run `scripts\portfolio_design_search.py recommend --input .resume-site-work\reports\content-map.json --output .resume-site-work\reports\design-intelligence.json`.
4. Read `references/design-intelligence-contract.md` and `reports\design-intelligence.json`. Use `selected_direction_id` as soft design intent; never turn Catalog output into fixed JSX, HTML, a fixed component tree, or a page template.
5. Read `references/creative-direction-contract.md`. From normalized facts, user-approved intent, and the design-intelligence candidates, compare two or three materially different creative layout families. Write `reports/creative-direction.json` with a fixed floor, open ceiling, and complete `concept_prototype`, then validate it before editing source:

```powershell
python "$SKILL_ROOT\scripts\validate_creative_direction.py" ".resume-site-work\reports\creative-direction.json"
```

6. Create a genuine React + Vite project at `.resume-site-work\site`. Implement the `concept_prototype` now: establish its `visual_protagonist`, express the selected family through `composition_commitment`, apply the initial `type_color_character`, and render the `representative_interaction_state`. Follow the prompt's five-region composition, centralized content data, media fallbacks, approximately 1700px desktop width, and accessibility requirements.
7. Run the `template_independence_test`: if removing final media and motion would leave a generic portfolio template, strengthen scale, rhythm, hierarchy, asymmetry, or the selected layout expression before presenting the prototype. Preserve every `creative_freedom.fixed` and `creative_freedom.avoid` entry while exploring the open ceiling. Reference-derived finishing, exact media treatment, and complex motion remains deferred.
8. Validate as `prototype`, build, promote the successful preview, and snapshot to `.resume-site-work\versions\v1-prototype` (or the next retry suffix).
9. Set `stage=prototype_waiting_confirmation`, show the built preview, and wait.

### Prototype confirmation gate

- On explicit confirmation, set `confirmations.prototype=true`, set `last_confirmed_artifact` to the candidate source snapshot, and advance to `media_direction_generating`.
- On rejection, record feedback and the current ID in `attempted_direction_ids`; select the next unused candidate before re-querying, regenerate from normalized inputs, and create a new retry snapshot.
- Do not enter media direction without confirmation.

## Stage 2: Direct and apply the media art direction

1. Read `references/design-intelligence-contract.md` and the current `reports\design-intelligence.json`. If the user provided a reference directory and `.resume-site-work\reference-library\manifest.json` is absent or stale, build it without touching the originals:

```powershell
python "$SKILL_ROOT\scripts\index_reference_library.py" `
  "<reference-directory>" `
  --workspace-root "."
```

2. When a reference-library manifest exists, inspect its `contact-sheets` with absolute Markdown image paths, then record selected source IDs and reasons in `reports/reference-selection.json`. Keep selected references at `usage_scope: "style_only"`; this evidence informs the internal media direction and never restores the old style confirmation gate.
3. Read `references/reference-library-contract.md`, `references/style-brief-schema.md`, `references/creative-direction-contract.md`, `reports/creative-direction.json`, `references/media-art-direction-contract.md`, `references/media-art-direction-schema.json`, `prompts/02-analyze-reference.md`, and `prompts/03-direct-media-art.md`; read a generated workspace manifest only when references exist.
4. Validate `media-direction` resources with `--workspace-root .`. A ready catalog does not substitute for unavailable media-direction resources.
5. Prepare a StyleBrief internally when references exist; it is input to media direction, never a separate user gate. It may enrich the creative direction's open ceiling, but must not silently change its fixed floor or avoid rules. If the report changes, revalidate it before source edits. Keep references at `usage_scope: "style_only"`; do not publish them as site assets without separate authorization.
6. Restore `.resume-site-work\versions\v1-prototype` into `.resume-site-work\site` when beginning or retrying this stage. Inspect the restored UI and authorized media, including each item's factual meaning and image role.
7. Always create `reports\media-inventory.json` before writing the direction report. It must be the trusted, versioned inventory of authorized media; when no media is authorized, write the explicit empty inventory `{"schema_version": 1, "assets": []}`.
8. Privately compare multiple media directions, exclude IDs in `attempted_media_direction_ids`, select exactly one winner, set `selected_media_direction_id`, and write `reports/media-art-direction.json` before editing source. Record structured `design_read`, `responsive_strategy`, and `reduced_motion_strategy` objects. Do not expose the internal comparison unless the user asks.
9. Implement exactly that winner in the same React + Vite project. Preserve all confirmed content facts and never use generated assets as factual evidence.
10. Validate `reports\media-art-direction.json` before validating the candidate as `media-direction`, then build it. Promote the preview only after all three succeed, so a failed attempt never replaces the last successful preview:

```powershell
python "$SKILL_ROOT\scripts\validate_media_art_direction.py" ".resume-site-work\reports\media-art-direction.json" --media-inventory ".resume-site-work\reports\media-inventory.json"
python "$SKILL_ROOT\scripts\validate_vite_project.py" ".resume-site-work\site" --stage media-direction
npm run build
```
11. Snapshot the successful source to `.resume-site-work\versions\v2-media-direction` (or retry suffix), set `stage=media_direction_waiting_confirmation`, and show one interactive candidate.

### Media direction confirmation gate

- On explicit confirmation, set `confirmations.media_direction=true`, update `last_confirmed_artifact`, and advance to `screenshot_auditing`.
- On rejection, restore `.resume-site-work\versions\v1-prototype`, record feedback and `selected_media_direction_id` in `attempted_media_direction_ids`, then return to `media_direction_generating` to implement one new winner.
- Do not start automatic screenshot repair without confirmation.

## Stage 3: Audit screenshots and repair local defects

1. Validate `screenshot` resources, then read `references/screenshot-review-rules.md`, `prompts/04-audit-screenshot.md`, and `prompts/05-repair-local-issues.md`.
2. Capture the successful built preview:

```powershell
python "$SKILL_ROOT\scripts\capture_site.py" ".resume-site-work\preview\dist\index.html" --output-dir ".resume-site-work\screenshots"
```

3. On capture exit `2`, show its dependency commands and request approval before installation. Retry capture infrastructure once without consuming a visual repair round.
4. Inspect desktop, tablet, and mobile screenshots plus `capture-report.json`; write schema-consistent findings to `reports/visual-audit.json`. Use the observable questions in `reports/creative-direction.json` to check whether the implementation preserves its fixed floor while expressing the selected creative thesis. Record `interaction_states_checked` evidence for the initial state and one representative active state per controller family, including each coarse-pointer/touch alternative and reduced-motion state. Exercise media loading, error, and Poster fallback states; check clipping, focus order, readability, image/UI cohesion, controller conflicts, and factual-media meaning.
5. For blocking or repairable findings with `visual_repair_round < 2`, edit only affected React/CSS regions in `.resume-site-work\site`, increment the round, validate as `refined`, build, promote, and recapture all viewports.
6. Preserve content, the confirmed media direction, and overall design direction. Do not rewrite the whole page for a local defect.
7. When no blocking findings remain, snapshot `.resume-site-work\versions\v3-refined`, update state, and advance automatically to `motion_generating`.
8. Treat essential-content loss, scroll traps, factual-media distortion, and absent fallbacks as blocking. After two completed repair rounds with blocking findings, set `stage=visual_blocked`, retain the last valid preview, and show unresolved defects. Do not present an incomplete page as complete.

Do not request routine confirmation during successful screenshot repair. This dynamic audit adds no confirmation step.

## Stage 4: Production-harden the confirmed motion layer

1. Validate `motion` resources, then read `references/motion-safety-rules.md`, `references/motion-production-contract.md`, and `prompts/06-add-motion.md`.
2. Restore the refined snapshot when beginning or retrying motion. Consume the confirmed media direction, `reports/creative-direction.json`, refined audit, and inventory of installed effect sources, effects, controllers, and dependencies. Use `motion_freedom.purpose`, `allowed`, and `avoid` as the motion brief. Preserve the confirmed visual thesis; do not redesign it.
3. Select only the sources the direction needs: CSS/native, React Bits, MotionSite, Motion, GSAP, and Three.js are available options, while React Bits is conditional. If React Bits is selected, register its official catalog and install exact `@react-bits` variants through the shadcn MCP.
4. Write `reports/motion-plan.json` before editing source. There is no numeric effect cap: merge compatible controllers into shared timelines or isolate sections. Each item needs a unique ID plus source, target, purpose, controllers, dependencies, conflict_resolution, cleanup, mobile, reduced_motion, and fallback.
5. Integrate only the planned source code in the same React + Vite project. Add lifecycle cleanup, coarse-pointer/mobile alternatives, static reduced-motion equivalents, and fallbacks. Do not restyle the page, rewrite resume content, or add runtime MCP dependence.
6. Validate as `motion`, build, promote, recapture all viewports, inspect layout stability and console errors, and verify mobile/coarse-pointer, reduced-motion, and Poster/media safety.
7. Snapshot `.resume-site-work\versions\v4-motion` (or retry suffix), set `stage=motion_waiting_confirmation`, show the animated preview and reduced-motion fallback, and wait.

### Motion confirmation gate

- Offer exactly two completion choices: `当前动效足够，完成` and `继续加强动效`.
- On `当前动效足够，完成`, set `confirmations.motion=true`, update `last_confirmed_artifact`, and set `stage=complete`.
- On `继续加强动效`, keep the production-hardened v4 snapshot as the confirmed baseline and set `stage=motion_enhancement_selecting`. Load MotionSite resources only after their approved local catalog is available.
- On rejection with specific motion feedback, restore `.resume-site-work\versions\v3-refined` (or the refined path recorded in state), revise only the motion plan/layer, and create a new retry snapshot.

## Stage 5: Add the optional recipe-based motion layer

1. Set `stage=motion_enhancement_selecting`. Validate `motion-enhancement` resources and read `references/motion-enhancement-contract.md`, `references/motion-recipe-schema.md`, `references/motion-media-slot-schema.md`, `references/video-embed-template.md`, and prompts 07–09.
2. Read only `assets/motion-enhancement/catalog/manifest.json`, shortlist compatible candidates, and load only the candidate recipe JSON files. Select multiple compatible primary recipes and multiple secondary effects when needed; there is no numeric effect cap. Validate the selection with `validate_motion_plan.py selection`, rejecting unknown/duplicate IDs and unresolved target/controller ownership.
3. Restore `.resume-site-work\versions\v4-motion`. Set `stage=motion_media_slot_planning`, preserve the confirmed page, and resolve the recipe placement reference into one site-specific media slot.
4. When the slot supports media, set `stage=motion_poster_generating`. Prefer a user-supplied image; otherwise generate a decorative theme-consistent Poster. Store it below `.resume-site-work\media\posters`, write `reports/motion-media-slot.json`, and validate it with `validate_motion_media.py`.
5. Poster generation is automatic when needed; user-supplied media is preferred. A user may request a replacement through ordinary feedback, which returns only to `motion_poster_generating`; it is not a confirmation state or a completion choice. Set `video_upgrade_available=true` after the Poster is retained.
6. Set `stage=motion_enhancement_generating`. Apply the selected recipe through `prompts/09-apply-motion-enhancement.md`; change only the motion/media layer and keep video playback passive.
7. Validate the project as `motion-enhanced`, run `npm run build`, capture desktop/tablet/mobile and reduced-motion states, and verify the Poster fallback.
8. Snapshot `.resume-site-work\versions\v5-motion-enhanced-poster`, return to `stage=motion_waiting_confirmation`, and show the enhanced preview with its reduced-motion fallback. The existing motion confirmation choice remains the only completion decision.

## Stage 6: Upgrade a confirmed Poster to video

This stage is available later whenever `stage=complete`, `video_upgrade_available=true`, and the user supplies a local MP4/WebM.

1. Set `stage=video_upgrade_validating`. Validate `video-upgrade` resources, read `references/video-upgrade-contract.md` and `prompts/10-upgrade-poster-to-video.md`, then run `validate_motion_media.py` against the confirmed Poster, supplied video, and media-slot report.
2. If validation is blocked or fails, keep the Poster preview active and report the exact issue. Do not edit source.
3. Restore `.resume-site-work\versions\v5-motion-enhanced-poster` and replace only the media component/assets. Keep the Poster as loading, error, mobile-budget, and reduced-motion fallback.
4. Validate as `video-upgrade`, run `npm run build`, capture all viewports, and verify that video is local, muted, looping, inline, passive, and resilient to errors.
5. On successful validation/build/capture, atomically promote the preview and snapshot `.resume-site-work\versions\v6-video-upgrade`, set `last_confirmed_video_artifact`, and return to `stage=complete` without another confirmation gate.
6. On validation, build, or capture failure, keep or restore the confirmed Poster preview and return to `stage=complete`; do not regenerate the website or Poster.

## Optional media search: APIHz images and GIFs

This branch begins only after an `explicit user request` for a meme, reaction image, humorous image, or GIF. It is available between normal stages and never becomes a required `prototype`, `media-direction`, `screenshot`, or `motion` resource.

1. Read `references/apihz-media-contract.md` and `prompts/11-search-optional-media.md`.
2. Confirm that `APIHZ_ID` and `APIHZ_KEY` exist in the process environment without printing their values. Operators may configure additional exact CDN hosts through `APIHZ_ASSET_HOSTS`.
3. Obtain a keyword of at most ten characters, or use random mode only when the user explicitly requests it. Run one search:

```powershell
python "$SKILL_ROOT\scripts\apihz_media.py" search --workspace-root "." --words "<keyword>" --limit 10
python "$SKILL_ROOT\scripts\apihz_media.py" search --workspace-root "." --random --limit 10
```

4. Show the absolute local `.resume-site-work\media-search\<search-id>\preview.html` path. Explain that static images and animated GIF candidates are `rights-unverified`; do not edit the React project yet.
5. Wait for explicit candidate IDs. Then run the selected-only import:

```powershell
python "$SKILL_ROOT\scripts\import_media_selection.py" --workspace-root "." --manifest ".resume-site-work\media-search\<search-id>\manifest.json" --select "media-a,media-b"
```

6. Use only imported `/assets/external/` paths in React, preserve GIF animation, and keep the selected site design direction. Never hotlink APIHz URLs or let a meme replace factual/user media.

`provider-failure isolation`: missing credentials, rate limits, unsafe URLs, unsupported files, or network failures leave the current site, preview, confirmations, snapshots, and `build-state.json` unchanged. Report the stable category and keep the normal workflow available.
## Invariants

- Persist `build-state.json` after every transition, successful candidate, rejection, and failure.
- Update `last_confirmed_artifact` only after explicit confirmation.
- Treat source validation, `npm run build`, and built-preview inspection as separate required checks.
- Keep reference images out of published content unless the user authorizes their use beyond style analysis.
- Preserve supplied facts and omit missing details instead of fabricating them.
- Treat `reports/creative-direction.json` as the intent boundary: preserve its
  fixed floor and avoid rules while keeping its open ceiling available for
  genuine visual exploration.
- Keep the main agent as integration owner for multi-agent work; shared files,
  workflow state, preview promotion, and snapshots are never delegated.
