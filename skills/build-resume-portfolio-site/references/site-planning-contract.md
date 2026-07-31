# Site Planning Contract

Begin only after schema-version-3 `site-design-spec.json` validates and its
final requirements confirmation is explicitly approved.

## Readable TODO plan

Create `.resume-site-work/reports/site-todo-plan.md` first. It must be concise
and readable in the conversation, with checkbox tasks covering:

- content mapping and overall structure;
- typography and color tokens;
- authorized media treatment and fallbacks;
- primary motion and every selected compatible secondary effect;
- component and exact file boundaries;
- responsive, accessibility, coarse-pointer, and reduced-motion behavior;
- validation, build, screenshots, bounded repair, rollback, and delivery.

Show the TODO plan, file scope, verification strategy, and expected artifacts.
Wait for explicit conversational TODO plan approval. A browser action, silence,
or approval of the design requirements is not plan approval.

## Machine plan

After approval, create schema-version-2
`.resume-site-work/reports/site-implementation-plan.json`. It records the
readable plan path and approval plus stable task IDs, dependencies, exact
writable files, consumed inputs, produced interfaces, acceptance criteria,
verification commands, rollback baseline, and `versions/v1-integrated`
snapshot target. Set `generation_mode` to `one-integrated-site`.

Select `single-agent`, `fresh-agent-sequential`, or `parallel-wave`.
Multi-agent strategies require explicit authorization and a separately
validated `multi-agent-implementation.json`.

Validate the JSON plan before any React source edit. If requirements change,
invalidate both planning artifacts, regenerate them, show the new TODO plan,
and obtain a new explicit approval.
