# Explicit Implementation Strategy Choice Design

## Goal

Require an explicit user choice between current-session single-Agent execution
and parallel multi-Agent execution after TODO-plan approval and before the
machine plan is written. The Skill recommends one option from the approved TODO,
file scope, and dependencies but never starts implementation until the user
chooses.

## Scope

This change affects implementation-strategy selection and corrects when each
independent browser-preview offer occurs. It does not change the six design
categories, requirements approval, TODO-plan approval, integrated site
generation, or final acceptance loop.

The user-facing choices are exactly:

1. `当前会话单 Agent`
2. `多 Agent 并行`

`fresh-agent-sequential` is removed as both a user-facing choice and an
implementation strategy for this Skill.

## Preview-before-selection correction

For every enabled visual category, browser preview is decision support and must
be offered before the user selects a candidate. Use this exact order:

1. compare candidates and recommend one with trade-offs;
2. separately ask whether to open an independent browser comparison;
3. on acceptance, show all candidates in a display-only Gallery; on decline,
   continue text-only;
4. ask the user to select a candidate or compatible secondary-motion set;
5. obtain explicit conversational confirmation; and
6. lock the category before continuing.

The Gallery may identify the Agent's recommendation but cannot mark a user
selection that has not happened. Browser visits, clicks, reloads, and launch
events still have no selection or approval semantics. Consent remains specific
to one category, including when the user declined or accepted a previous offer.

This ordering applies to structure, typography, color, conditional media,
primary motion, and secondary motion. A media category that is explicitly
skipped because no media strategy is applicable has no preview offer.

## Decision flow

After the readable TODO plan is explicitly approved, the main Agent evaluates
its tasks, exact file scope, and dependencies before writing the
schema-version-2 implementation plan or editing React source.

It then presents:

1. one recommended execution mode;
2. concrete reasons derived from the current plan;
3. the expected coordination and speed trade-off;
4. the two numbered choices; and
5. a request for an explicit `1` or `2` reply.

Silence, prior authorization, TODO approval, requirements approval, browser
activity, or an inferred preference cannot select an execution mode. The
workflow remains in `implementation_strategy_waiting_confirmation` until the
conversation contains an explicit choice.

## Recommendation rules

Recommend `当前会话单 Agent` when any of these conditions applies:

- work is concentrated in shared files such as `App.jsx`, global styles,
  centralized content data, or package configuration;
- task outputs are tightly coupled or require frequent visual iteration;
- fewer than two independently useful tasks can run concurrently;
- proposed write ownership overlaps;
- coordination, integration, or repeated validation is likely to cost at least
  as much time as parallel execution saves; or
- parallel speedup cannot be demonstrated from the implementation plan.

Recommend `多 Agent 并行` only when all of these conditions hold:

- at least two tasks are independently useful;
- their write sets are disjoint;
- dependencies permit the tasks to run in the same wave;
- each task has independent acceptance criteria;
- shared files, state, preview promotion, snapshots, and publication remain
  owned by the main Agent; and
- expected parallel savings clearly exceed dispatch, review, and integration
  overhead.

The recommendation is advisory. The user makes the final selection, subject to
the safety constraint below.

## Selection behavior

For `当前会话单 Agent`, write `single-agent` into the machine plan, validate the
plan, and continue in the current conversation without dispatching subagents.

For `多 Agent 并行`, require explicit conversational authorization, write
`parallel-wave` into the machine plan, then write and validate both the machine
plan and `reports/multi-agent-implementation.json` before dispatch. Every task
must have bounded scope and disjoint file ownership. The main Agent remains
responsible for shared files, workflow state, integration, validation, preview
promotion, snapshots, and publication.

If the user selects parallel execution but the validated plan cannot satisfy
the parallel-safety rules, do not spawn agents. Explain the concrete conflict
and ask the user either to approve a revised disjoint plan or select
`当前会话单 Agent`. This is a safety correction, not an automatic fallback.

## State and validation

Add an explicit waiting state between plan validation and integrated generation:

```text
todo_plan_waiting_confirmation
--approve--> implementation_strategy_waiting_confirmation
implementation_strategy_waiting_confirmation
--choose 1--> implementation_plan_generating with single-agent
implementation_strategy_waiting_confirmation
--choose 2--> implementation_plan_generating with parallel-wave
implementation_strategy_waiting_confirmation
--choose 2 and plan conflicts--> implementation_strategy_waiting_confirmation
implementation_plan_generating
--machine plan validates--> integrated_generating
implementation_plan_generating
--parallel selected and either plan fails--> implementation_strategy_waiting_confirmation
```

The implementation-plan validator continues to accept `single-agent` and
`parallel-wave`, but rejects `fresh-agent-sequential`. A parallel plan still
requires explicit user authorization and separate multi-Agent plan validation.

## User-facing presentation

Use this output shape, adapted to the actual plan:

> 执行方式推荐：当前会话单 Agent
>
> 原因：本次任务集中修改共享组件和全局样式，多 Agent 的协调成本预计高于并行收益。
>
> 1. 当前会话单 Agent
> 2. 多 Agent 并行
>
> 请明确选择 1 或 2。

Do not bury the recommendation after the options and do not present additional
execution modes.

## Failure and recovery

- Missing selection: keep waiting; make no source edits and spawn no agents.
- Ambiguous reply: restate the two choices and request `1` or `2`.
- Unsafe parallel selection: show overlapping files or unresolved dependencies,
  then wait for a revised plan or a new selection.
- Parallel validation failure: preserve approvals and artifacts, record exact
  diagnostics, and remain at the strategy gate.
- Dispatch or task failure: retain main-Agent ownership and the last valid
  artifact; do not promote partial output.

## Testing

Behavior tests must prove that the Skill:

- offers each enabled category's browser comparison before requesting a choice;
- never describes the Gallery as showing a tentative user selection;
- presents exactly the two user-facing choices;
- recommends from observable plan characteristics;
- waits for explicit conversational selection;
- does not treat earlier approval as strategy authorization;
- removes `fresh-agent-sequential` from runtime contracts and schemas;
- recommends single-Agent when parallel benefit is uncertain;
- blocks unsafe parallel dispatch instead of silently falling back; and
- preserves main-Agent ownership for shared integration responsibilities.

Run the focused strategy tests first, then the complete repository and Skill
test suites, resource validation, and Skill quick validation. After verification,
synchronize the source Skill to the global installed directory and compare file
sets and hashes.
