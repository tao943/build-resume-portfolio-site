# Upfront Portfolio Design Decisions

## Goal

Change full site discovery so the user confirms the complete design intent before React source generation. Discovery must cover structure, typography, color, conditional media treatment, primary motion, and secondary motion. Each decision may receive its own independent browser preview. After the requirements are confirmed, the Skill must generate and obtain approval for a readable TODO plan before producing the website once.

## Scope

This design applies to new sites and changes that alter structure, visual direction, interaction architecture, or implementation strategy. Bounded existing-site changes continue to use the fast-change route unless their scope expands into one of these design decisions.

The browser remains a display-only companion. Selection and approval occur only in the conversation.

## Discovery sequence

Full discovery uses this fixed order:

1. Overall structure
2. Typography and typesetting character
3. Color system
4. Media treatment, only when authorized media exists or the user wants a media strategy
5. Primary motion
6. Secondary motion
7. Final requirements confirmation
8. TODO plan generation and approval
9. One-pass website generation

Responsive behavior, accessibility, coarse-pointer support, and reduced-motion behavior are engineering constraints rather than optional user choices.

## Decision transaction

Each enabled design category follows the same transaction:

1. Derive two or three materially different candidates from the approved content and constraints.
2. Explain the candidates, recommend one, and state the important trade-offs.
3. Receive a tentative conversational selection.
4. Ask, in a separate prompt, whether the user wants to open a browser for this category's visual preview.
5. If accepted, generate and present an independent display-only gallery. If declined, record the decline and continue text-only.
6. Receive explicit confirmation, revision, or rejection in the conversation.
7. Lock the confirmed decision before entering the next category.

The preview-offer question is required even when the candidates can be described in text. Do not infer consent from a previous preview: the user decides separately for every category. Do not repeatedly offer the same category after the user declines.

## Independent preview model

The six previews are independent, not cumulative. Each gallery isolates one decision dimension using a neutral demonstration baseline:

- structure previews compare composition, hierarchy, navigation, and content density;
- typography previews compare type character, scale, rhythm, and reading texture;
- color previews compare background, foreground, accent, contrast, and semantic color roles;
- media previews compare framing, cropping, sequencing, fallback, and image-to-interface relationships;
- primary-motion previews compare the main temporal or scroll narrative;
- secondary-motion previews compare compatible local feedback and atmosphere effects.

An independent preview is evidence for a decision, not reusable React source and not a fragment to be concatenated into the final website. The gallery shows all candidates and may visually mark the tentative selection, but it contains no selection controls, approval buttons, analytics, or event collection.

Browser launch failure is non-blocking. The Skill must provide the authenticated local URL when available and the absolute static HTML fallback. Browser visits, reloads, screenshots, or automatic opening never advance workflow state.

## Primary and secondary motion

Primary motion defines the site's dominant motion system, such as scroll-driven narrative, sectional transitions, spatial parallax, or staged reveals. Exactly one primary system is selected so multiple top-level timelines do not compete for control.

Secondary motion provides local response and atmosphere, such as button feedback, card hover, text reveal, cursor response, background particles, or light media parallax. The user may select multiple secondary effects without a fixed numeric cap. Before presenting them, the Skill filters candidates for compatibility with the primary motion, controller ownership, mobile/coarse-pointer behavior, performance, cleanup, fallback, and reduced-motion behavior.

## Requirements package

After all enabled categories are confirmed, the Skill writes a schema-version-3 site design specification containing:

- all candidates, recommendation, tentative selection, and final selection for each category;
- the category's conversational approval evidence;
- whether the browser preview was offered, accepted, declined, or unavailable;
- gallery and launch evidence when a preview was produced;
- an explicit media-stage skip reason when applicable;
- primary/secondary motion compatibility results;
- required responsive, accessibility, fallback, and reduced-motion constraints.

The Skill then presents a consolidated requirements summary. The user must explicitly confirm that summary before planning begins. Changing a core decision invalidates the consolidated confirmation and any existing implementation plan.

## TODO plan gate

After final requirements confirmation, the Skill generates two synchronized planning artifacts:

1. A concise, human-readable TODO plan covering content mapping, page structure, design system, media, primary and secondary motion, component/file ownership, responsive behavior, accessibility, build verification, screenshot review, rollback, and final delivery.
2. A machine-validatable `site-implementation-plan.json` containing exact files, dependencies, interfaces, acceptance criteria, verification commands, rollback baseline, and snapshot target.

The Skill shows the TODO plan, relevant file scope, verification strategy, and expected artifacts in the conversation. React source must not be created or edited until the user explicitly approves the plan and the JSON plan validates. A changed requirement requires regenerating and reapproving both artifacts.

## One-pass website generation

After plan approval, the Skill generates the complete React + Vite website in one implementation transaction. Structure, typography, color, media treatment, primary motion, and secondary motion are applied together from the approved requirements package.

The implementation may run automated validation, build, responsive screenshots, accessibility checks, and bounded local repairs without intermediate design confirmation. It must not silently select a different design direction or reopen completed discovery decisions.

The first user-facing website candidate is the complete integrated site rather than a sequence of prototype, media-direction, and motion confirmation stages.

## Final acceptance loop

After the integrated site passes validation and is presented, offer three outcomes:

1. `当前效果满意，完成`
2. `加强动效`
3. `提出修改`

`加强动效` preserves approved content, structure, typography, color, and media treatment. It reopens only primary/secondary motion planning and implementation against the last valid integrated snapshot.

`提出修改` routes bounded feedback to local repair. Feedback that reverses a core design decision returns to that decision category, invalidates downstream requirements and plans, and requires a new requirements confirmation and TODO-plan approval before regeneration.

## State and rollback

The workflow state records the active category, category decisions, preview-offer results, final requirements confirmation, TODO-plan approval, implementation attempt, last valid integrated preview, and last confirmed artifact.

Failures preserve the last valid artifact:

- preview failure falls back to static HTML or text-only confirmation;
- planning failure prevents source edits;
- build or screenshot failure retains the previous valid preview and permits bounded repair;
- motion enhancement begins from the last valid integrated snapshot;
- a core decision change invalidates only its downstream decisions and artifacts.

## Validation strategy

Behavior and schema tests must prove that:

- categories occur in the required order;
- the media category can be skipped only with an explicit reason;
- every enabled category asks separately whether to open a browser preview;
- declining one preview does not suppress later preview offers;
- all galleries remain display-only and independent;
- primary motion is singular and secondary motion supports compatible multi-selection;
- final requirements confirmation is required before planning;
- a readable TODO plan and valid JSON plan both exist and receive explicit approval before source edits;
- the first generated React candidate integrates all confirmed decisions;
- motion enhancement preserves non-motion decisions;
- core-decision changes invalidate and regenerate downstream planning artifacts.

## Migration

Schema-version-2 discovery reports remain readable evidence but do not satisfy the new full-discovery gate. Existing confirmed sites may continue through a validated bounded fast-change route. A new full design or regenerated site must use schema version 3 and the new requirements and TODO-plan approvals; the Skill must not fabricate missing approvals during migration.
