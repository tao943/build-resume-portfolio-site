# Multi-Agent Implementation Contract

Use this contract only after the user explicitly selects `多 Agent 并行`. It is
an implementation strategy inside the existing workflow, not a new portfolio
stage or confirmation gate.

## Strategy selection

The only multi-Agent strategy is `parallel-wave`. Use it only after the user
explicitly selects `多 Agent 并行` and both the site implementation plan and
multi-Agent plan validate. Require at least two independently useful tasks in a
parallel wave with disjoint write ownership and independent acceptance checks.

Sequential waves may be used only for integration and dependent review inside
the selected parallel strategy; they are not a separate user-facing mode.
Never split work by page or section merely to increase agent count. If the
parallel criteria cannot be met, return to the strategy gate and ask the user
to approve a revised disjoint plan or select `当前会话单 Agent`.

## Controller and ownership

The main agent is always the visual director, controller, integration owner,
and publisher. It owns the approved design thesis, current workflow stage,
`build-state.json`, preview promotion, snapshots, package dependencies, and
final acceptance.

Before dispatch, write
`.resume-site-work/reports/multi-agent-implementation.json` against
`multi-agent-implementation-schema.json`, then run:

```powershell
python "$SKILL_ROOT\scripts\validate_multi_agent_plan.py" `
  ".resume-site-work\reports\multi-agent-implementation.json"
```

Continue only on exit `0`. The plan must define task dependencies, waves,
allowed files, acceptance checks, and verification commands. There is no
overlapping file ownership inside a parallel wave.

Treat `App.jsx`, global CSS or design tokens, central data contracts,
`package.json`, `build-state.json`, reports, preview output, and version
snapshots as shared files unless the project proves otherwise. Only a task with
role `integration` may write shared files. If a supposedly independent task
needs a shared file, submit a handoff request to the integration owner. Do not
silently change the user's selected execution mode.

## Task packet

Give each implementation agent a bounded packet:

1. the creative thesis plus relevant fixed floor, open ceiling, avoid rules,
   review questions, and facts it must preserve;
2. exact allowed files and explicit forbidden shared files;
3. dependencies and frozen interfaces it consumes;
4. acceptance criteria and the smallest relevant verification;
5. instruction to report changed files, checks run, unresolved risks, and
   integration requests.

Agents do not update workflow state, promote previews, create snapshots, install
dependencies, or reinterpret user approval. A blocked task reports the exact
dependency and stops.

## Waves and reviews

Complete all dependencies before starting a wave. Parallel tasks may run
together only when their write sets are disjoint. At each wave boundary, the
main agent checks the task reports and working tree before continuing.

Use two review lenses after integration:

1. specification review checks the implementation against the approved brief,
   content facts, media direction, and task acceptance criteria;
2. quality audit checks code quality, responsive behavior, accessibility,
   media fallbacks, motion safety, and regressions.

Review and audit tasks are independent and read-only. They report findings with
severity and exact file locations; they never silently repair source. Route
repairs back to the original file owner, while shared-file repairs remain with
the integration owner.

## Final integration

The main agent resolves cross-task conflicts and then executes the original
stage transaction once: project validation, `npm run build`, required captures
and dynamic-state checks, preview promotion, immutable snapshot, and state
update. A subtask's local success never authorizes publication. On failure,
keep the previous valid preview and confirmed snapshot active.

Record concise task reports under
`.resume-site-work/agent-reports/<task-id>.md`. These reports are working
evidence, not new user confirmation gates.
