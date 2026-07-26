# Superpowers-Style Workflow Internalization Design

## Goal

Internalize the useful behavior of Superpowers-style brainstorming and
implementation planning into the `resume-portfolio-workflow` plugin without
requiring users to install Superpowers separately.

The plugin must keep both domain skills independently callable:

- `resume-content-intelligence`
- `build-resume-portfolio-site`

Installing the plugin once must make the complete content-to-site workflow
available.

## Selected Architecture

Use a hybrid architecture:

1. Add a thin `resume-portfolio-workflow` orchestration skill.
2. Give each domain skill its own domain-specific discovery and planning
   contracts.
3. Enforce the contracts with structured reports and validators.

The orchestration skill owns cross-skill routing. The domain skills retain
their own gates so direct invocation cannot bypass discovery, approval, or
planning.

No runtime dependency on the external `brainstorming`, `writing-plans`,
`executing-plans`, or `subagent-driven-development` skills is allowed.

## Workflow Modes

### Full workflow

Use the full workflow when any of these observable conditions is true:

- creating a new content package;
- creating a new website;
- changing audience, positioning, narrative, or target role;
- changing the overall visual direction;
- adding or removing a page, section, interaction family, or major behavior;
- introducing a new implementation strategy or multi-agent boundary.

The full sequence is:

1. Inspect existing materials, state, and confirmed artifacts.
2. Ask one decision-bearing question at a time.
3. Compare two or three materially different approaches.
4. Recommend one approach with explicit trade-offs.
5. Present a domain design specification.
6. Wait for explicit user approval.
7. Write and validate a domain implementation plan.
8. Select the implementation strategy.
9. Implement through the existing controlled stages.
10. Verify, snapshot, and retain the last confirmed artifact.

### Fast-change workflow

Use the fast-change workflow only when all of these conditions are true:

- an existing confirmed artifact is available;
- the user requested a bounded local change;
- facts, audience, structure, visual thesis, and interaction architecture do
  not change;
- the affected files and verification method can be stated before editing.

The fast-change brief records:

- requested outcome;
- preserved constraints;
- exact affected region or files;
- verification command or observable check;
- rollback baseline.

Copy corrections, replacing one authorized asset, and repairing a reproducible
local visual defect may use this workflow. A request that expands while being
implemented must return to the full workflow before further source edits.

## Orchestration Skill

Add `skills/resume-portfolio-workflow/SKILL.md`.

It must:

- decide whether content preflight is required;
- route factual and copy work to `resume-content-intelligence`;
- route confirmed content to `build-resume-portfolio-site`;
- preserve approval and provenance boundaries across the handoff;
- detect full-workflow versus fast-change conditions;
- never edit React source or approved content itself.

The orchestration skill is a router, not a third implementation owner.

## Content Skill Internalization

Add:

- `references/content-brainstorming-contract.md`
- `references/content-planning-contract.md`
- `references/content-design-spec-schema.json`
- `references/content-implementation-plan-schema.json`
- `scripts/validate_content_design_spec.py`
- `scripts/validate_content_implementation_plan.py`

The content discovery process must:

- inventory evidence before asking questions;
- ask one question at a time;
- prioritize identity, dates, scope, outcomes, metrics, and target-role
  decisions;
- compare two or three content strategies when positioning or narrative is
  genuinely open;
- separate facts, inference, proposed copy, and approved copy;
- wait for explicit approval of the content design specification before
  producing an implementation plan.

The content plan must identify:

- evidence and fact IDs consumed;
- copy blocks to create or revise;
- questions or unsupported claims that remain blocked;
- target files in the content package;
- validation commands and expected outcomes;
- handoff criteria for the website skill.

The resulting reports are:

- `.resume-site-work/reports/content-design-spec.json`
- `.resume-site-work/reports/content-implementation-plan.json`

Content approval remains a separate later gate. Approving the design strategy
does not automatically approve final resume copy.

## Website Skill Internalization

Synchronize the plugin copy with the newer installed website skill before
adding the new contracts. Preserve its content preflight, creative-direction,
multi-agent, screenshot-audit, media, and motion behavior.

Add:

- `references/site-brainstorming-contract.md`
- `references/site-planning-contract.md`
- `references/site-design-spec-schema.json`
- `references/site-implementation-plan-schema.json`
- `scripts/validate_site_design_spec.py`
- `scripts/validate_site_implementation_plan.py`

The site discovery process must:

- inspect confirmed content, authorized media, existing site state, and
  references;
- ask one design decision at a time;
- compare two or three materially different layout or experience families;
- define the visual protagonist, composition commitment, type and color
  character, representative interaction, fixed constraints, open creative
  ceiling, and avoid rules;
- wait for explicit approval before creating or structurally redesigning React
  source.

The site implementation plan must identify:

- exact files to create or modify;
- task boundaries and dependencies;
- interfaces produced and consumed by each task;
- validation and screenshot evidence required;
- rollback and snapshot boundaries;
- single-agent, fresh-agent-sequential, or parallel-wave strategy;
- file ownership for every multi-agent task.

The resulting reports are:

- `.resume-site-work/reports/site-design-spec.json`
- `.resume-site-work/reports/site-implementation-plan.json`

The existing `creative-direction.json` remains the visual intent contract.
`site-design-spec.json` records the user-approved product and experience
decision; `creative-direction.json` translates it into implementation-ready
visual direction. They must not contradict each other.

## Approval Gates

The full workflow has these distinct approvals:

1. Content strategy approval, when content work is required.
2. Final content/copy approval.
3. Website design specification approval.
4. Existing prototype, media-direction, and motion confirmations.

Implementation-plan creation follows design approval automatically. The plan
must be shown to the user before implementation begins, but a second approval
is only required when the plan introduces a new dependency, external service,
destructive operation, public publication, or multi-agent execution.

## State and Migration

Update the website workflow state to schema version `4`.

Provide a one-way validator-backed migration from schema version `3` to `4`.
The migration must:

- preserve existing confirmations, snapshot paths, previews, attempted
  direction IDs, and repair counts;
- derive no new user approval;
- mark new discovery and planning approvals as incomplete unless equivalent
  confirmed artifacts already exist;
- retain existing confirmed sites for fast-change work;
- refuse malformed or ambiguous state instead of guessing.

The content reports remain independently validated and do not become factual
evidence merely because they exist.

## Multi-Agent Execution

Multi-agent work remains optional and requires explicit user authorization.

Planning must happen before agent dispatch. The main agent remains:

- workflow-state owner;
- design director;
- shared-file owner;
- integration owner;
- preview and snapshot promoter.

Parallel agents receive disjoint file ownership and independently useful
tasks. Sequential fresh agents may be used where fresh context is valuable but
task dependencies prevent parallel work.

## Validation and Failure Behavior

Every new structured report must have:

- a JSON schema or equivalent explicit contract;
- a validator with stable exit codes;
- unit tests for valid, missing-field, contradictory, and unsafe inputs;
- failure isolation that leaves the last confirmed preview and state intact.

Validation must reject:

- placeholder text such as `TODO` or `TBD`;
- empty alternatives disguised as multiple approaches;
- plans without exact file ownership or verification;
- inferred user approval;
- unsupported factual claims;
- parallel tasks with overlapping writable files;
- fast-change classification when structural or strategic scope changed.

## Skill-Level RED/GREEN Tests

Before changing the skill instructions, record baseline failures using the
current plugin copy. At minimum, cover:

1. A rushed new-site request that pressures the agent to skip design approval.
2. A resume rewrite request that pressures the agent to invent a metric.
3. A vague redesign request where alternatives collapse into one generic
   layout.
4. A multi-agent request with overlapping file ownership.
5. A small copy correction that should not trigger the full workflow.

After implementation, repeat equivalent scenarios and verify that:

- full-scope requests stop at the correct approval gate;
- factual uncertainty remains visible;
- plans contain exact files, dependencies, and checks;
- small bounded changes use the fast lane;
- no external Superpowers skill is required.

## Packaging and Distribution

The GitHub repository remains a Codex plugin:

```text
.codex-plugin/plugin.json
skills/
  resume-portfolio-workflow/
  resume-content-intelligence/
  build-resume-portfolio-site/
```

The distributable ZIP must contain the plugin manifest and all three skills
when intended for one-click plugin installation. A separate skills-only ZIP
may continue to contain only `skills/` for manual inspection or installation.

Before publication:

- run all new validators and focused tests;
- run the plugin validator;
- scan for credentials and local private data;
- rebuild the ZIP;
- commit and push the validated source.

## Success Criteria

The change is complete when:

- installation exposes all three skill names;
- direct invocation of either domain skill preserves its own discovery and
  planning gates;
- the orchestrator completes the content-to-site handoff;
- new sites cannot edit source before design approval and plan validation;
- bounded existing-site changes remain lightweight;
- the plugin has no runtime dependency on Superpowers;
- validators, focused tests, plugin validation, ZIP inspection, and sensitive
  information scanning pass.
