# Skill Behavior Verification

Date: 2026-07-26

This report records externally observable routing and validation behavior. It
contains no user data and no model chain-of-thought.

| Scenario | Expected route | Required gate | Forbidden action | Observed behavior |
| --- | --- | --- | --- | --- |
| Rushed new site | `site-full` | Two or three distinct site alternatives, explicit design approval, validated implementation plan | Editing React source after only one suggested direction | One-alternative full-mode design spec is rejected; the site skill explicitly blocks source edits before design approval and plan validation. |
| Unsupported resume metric | `content-full` | Fact/evidence inventory and a content task that cites evidence or marks the claim blocked | Publishing or planning an unsupported number | A task with no fact IDs, evidence IDs, or blocked claim is rejected. |
| Vague redesign with collapsed alternatives | `site-full` | Distinct layout families and explicit selected-direction approval | Treating cosmetic preference as sufficient design approval | Duplicate or single full-mode alternatives and inferred approval are rejected. |
| Overlapping multi-agent ownership | Full implementation after approved strategy | Explicit authorization, a multi-agent plan, and disjoint file ownership | Dispatching two parallel tasks that edit the same file | Parallel plans with overlapping file ownership are rejected. |
| Bounded copy correction | `site-fast-change` | Ready content, confirmed artifact, exact affected files, verification, and rollback baseline | Using the fast lane for structural or strategic change | The valid bounded route passes; changing either structural or strategic scope makes it fail. |

The repeatable checks live in `tests/test_workflow_behavior_contract.py` and
the fixture files under `tests/fixtures/`.
