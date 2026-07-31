---
name: build-resume-portfolio-site
description: Use when creating or redesigning a runnable React + Vite resume or portfolio site from approved resume content, portfolio materials, visual references, screenshots, or an existing confirmed site.
---

# Build Resume Portfolio Site

Confirm the complete design intent and implementation plan before generating
one integrated React + Vite portfolio. Preserve user facts, edit one source
project, and retain the last valid source snapshot.

## Start or resume

1. Resolve `SKILL_ROOT` as this Skill directory.
2. Read `references/workflow-contract.md`, `references/artifact-layout.md`,
   `references/content-preflight-routing-contract.md`,
   `references/site-brainstorming-contract.md`,
   `references/visual-style-preview-contract.md`,
   `references/site-planning-contract.md`,
   `references/react-vite-output-contract.md`,
   `references/design-intelligence-contract.md`,
   `references/creative-direction-contract.md`,
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

   - `CONTENT_READY` continues.
   - `ROUTE_REQUIRED` requires `resume-content-intelligence`, its user approval,
     and a new handoff before retrying.
   - `CONTENT_INVALID` freezes source, preview, snapshots, and state until fixed.
5. Use `.resume-site-work/site` as the only editable React + Vite project. A
   discovery Gallery is evidence, never a second website source.

## Full discovery gate

Use the full route for a new site or a change to audience, overall structure,
visual thesis, interaction architecture, or implementation strategy.

1. Validate `discovery` resources.
2. Inspect approved content, authorized media, references, and confirmed state.
3. Ask one question at a time and complete these categories in exact order:
   overall structure, typography, color system, conditional media treatment,
   primary motion, and secondary motion.
4. For every enabled category, compare candidates, recommend one, receive a
   tentative choice, then separately ask whether to open a browser preview.
5. On acceptance, follow `visual-style-preview-contract.md`, create an
   independent display-only `gallery.html`, run `launch.cjs --open`, and give
   the user the complete authenticated URL plus the absolute static HTML fallback. On decline, continue text-only. Previous consent never applies to
   the next category.
6. Receive final category confirmation in the conversation. Approval remains in the conversation: browser visits, reloads, screenshots, and launch events
   do not select, approve, or advance state.
7. Media may be skipped only with an explicit reason. Select exactly one
   primary-motion system. Secondary motion may contain multiple compatible
   effects without a fixed numeric cap.
8. Summarize all decisions and mandatory responsive, accessibility,
   coarse-pointer, fallback, and reduced-motion constraints. Obtain final
   requirements confirmation.
9. Write schema-version-3
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
5. Write schema-version-2
   `.resume-site-work/reports/site-implementation-plan.json` with
   `generation_mode: one-integrated-site`, exact tasks, dependencies, files,
   interfaces, acceptance, verification, rollback, and `versions/v1-integrated`.
6. Validate the plan:

```powershell
python "$SKILL_ROOT\scripts\validate_site_implementation_plan.py" `
  ".resume-site-work\reports\site-implementation-plan.json"
```

Do not edit React source before final requirements approval, explicit TODO plan
approval, and successful JSON plan validation. A changed core decision
invalidates final requirements approval and both planning artifacts.

## Select the implementation strategy

Choose only after the plan gate:

- `single-agent` for local or tightly coupled work;
- `fresh-agent-sequential` for an authorized dependency chain;
- `parallel-wave` only for authorized independent tasks with disjoint files.

Multi-agent execution requires explicit user authorization and a validated
`multi-agent-implementation.json`. The main agent owns shared files, state,
integration, preview promotion, snapshots, and publication.

## Generate one integrated website

1. Set `stage=integrated_generating` and validate `integrated` resources.
2. Read `prompts/01-generate-integrated-site.md`.
3. Generate `reports/content-map.json` only from normalized facts and approved
   copy. Create or refresh `reports/design-intelligence.json` as soft guidance.
4. Translate the approved six decisions into implementation detail without
   changing them. Create supporting media-direction, creative-direction, and
   motion reports when applicable.
5. Create or replace the complete source at `.resume-site-work/site` in one
   integrated transaction. Apply structure, typography, color, media treatment,
   one primary-motion system, and all selected compatible secondary effects.
6. Validate and build:

```powershell
python "$SKILL_ROOT\scripts\validate_vite_project.py" `
  ".resume-site-work\site" --stage integrated
npm run build
```

7. On success, atomically promote `site/dist` to `preview/dist`, capture desktop,
   tablet, mobile, representative interaction, coarse-pointer, and reduced-motion
   states, and inspect console/layout/media safety.
8. Perform at most two bounded local repair rounds. Do not silently change a
   confirmed design decision. Keep the previous valid preview on failure.
9. Snapshot successful source to `versions/v1-integrated` or a retry suffix,
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
treatment. Re-plan controller ownership, mobile/coarse-pointer behavior,
cleanup, fallback, and reduced motion; validate/build/capture, snapshot a retry,
then return to `integrated_waiting_confirmation`.

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

- APIHz search begins only on an explicit user request. Keep candidates local,
  rights-unverified, and outside React until the user names IDs. Provider
  failure leaves site, preview, approvals, snapshots, and state unchanged.
- A later user-supplied local MP4/WebM may replace only an approved Poster/media
  slot. Keep the Poster as loading, error, mobile-budget, and reduced-motion
  fallback; validate/build/capture before promoting.

## Invariants

- Persist state after every transition, rejection, and failure.
- Only conversation replies provide approval evidence.
- Source validation, build, and built-preview inspection are separate checks.
- Never publish reference-only media or fabricate facts, metrics, people, or
  project images.
- Preserve the last valid preview and immutable source snapshot on failure.
- No external Superpowers skill is required at runtime.
