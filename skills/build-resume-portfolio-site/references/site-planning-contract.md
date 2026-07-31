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

## Implementation strategy gate

After TODO approval, evaluate the approved tasks, exact file scope,
dependencies, shared-file coupling, independently useful work, and coordination
cost. Recommend `当前会话单 Agent` or `多 Agent 并行` with plan-specific evidence
and the expected speed trade-off. If parallel speedup cannot be demonstrated,
recommend `当前会话单 Agent`.

Present exactly the two numbered choices and ask the user to explicitly choose
`1` or `2`. Set `stage=implementation_strategy_waiting_confirmation` and wait.
Silence, browser activity, inferred preference, design approval, or TODO approval
is not strategy selection.

Use `single-agent` for choice `1`. Use `parallel-wave` for choice `2` only when
at least two independently useful tasks have disjoint writes, compatible
dependencies, independent acceptance criteria, and expected savings greater
than coordination cost. Unsafe parallel work remains at the gate until the
user approves a revised disjoint plan or makes a new explicit choice.

## Machine plan

After explicit strategy selection, create schema-version-2
`.resume-site-work/reports/site-implementation-plan.json`. It records the
readable plan path and approval plus stable task IDs, dependencies, exact
writable files, consumed inputs, produced interfaces, acceptance criteria,
verification commands, rollback baseline, and `versions/v1-integrated`
snapshot target. Set `generation_mode` to `one-integrated-site` and record:

```json
"strategy_selection": {
  "status": "user_selected",
  "source": "explicit_user",
  "channel": "conversation",
  "selected": "single-agent",
  "recommended": "single-agent",
  "reasons": ["Plan-specific recommendation evidence."]
}
```

The `selected` value must match `strategy`. Parallel execution requires explicit
authorization and a separately validated `multi-agent-implementation.json`.

Validate the JSON plan before any React source edit. If requirements change,
invalidate both planning artifacts, regenerate them, show the new TODO plan,
obtain a new explicit approval, and repeat the strategy gate.
