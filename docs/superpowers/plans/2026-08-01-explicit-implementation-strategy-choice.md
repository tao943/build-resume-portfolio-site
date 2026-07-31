# Explicit Implementation Strategy Choice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the portfolio Skill recommend and display exactly `当前会话单 Agent` or `多 Agent 并行`, then block implementation until the user explicitly chooses one.

**Architecture:** Move strategy selection between readable TODO approval and machine-plan generation. Persist the recommendation and explicit conversational selection in a required `strategy_selection` object inside the schema-version-2 machine plan. Keep only `single-agent` and `parallel-wave`; parallel execution additionally requires the existing validated multi-Agent plan.

**Tech Stack:** Markdown Skill contracts, JSON Schema Draft 2020-12, Python 3 `unittest` validators, PowerShell verification, Git.

## Global Constraints

- Present exactly two user-facing choices: `当前会话单 Agent` and `多 Agent 并行`.
- For every enabled visual category, ask whether to open its independent browser comparison before requesting the user's candidate selection.
- A pre-selection Gallery may mark the Agent recommendation but never a user selection that has not occurred.
- Recommend from approved TODO tasks, exact file scope, dependencies, coupling, and expected coordination cost.
- When parallel speedup cannot be demonstrated, recommend `当前会话单 Agent`.
- Silence, prior approvals, browser activity, or inferred preference never select a strategy.
- Do not write the machine plan, edit React source, or spawn agents before explicit strategy selection.
- Remove `fresh-agent-sequential` from active Skill contracts and validator schemas.
- Parallel execution requires at least two independently useful tasks, disjoint write sets, independent acceptance criteria, explicit authorization, and main-Agent integration ownership.
- An unsafe parallel choice remains at the strategy gate until the user approves a revised disjoint plan or selects single Agent; never silently fall back.
- Preserve the six design decisions, separate preview offers, TODO approval, one integrated generation transaction, and final three-outcome acceptance loop.

---

### Task 1: Define the two-choice workflow behavior

**Files:**
- Modify: `tests/test_workflow_behavior_contract.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_installed_skill_workflow.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_synced_workflow_baseline.py`

**Interfaces:**
- Consumes: current `SKILL.md`, `workflow-contract.md`, and `site-planning-contract.md` text.
- Produces: failing behavioral assertions for the exact two choices, recommendation rules, explicit waiting gate, and retired sequential strategy.

- [ ] **Step 1: Add failing repository behavior tests**

Add these methods to `WorkflowBehaviorContractTests`:

```python
def test_strategy_gate_offers_exactly_two_explicit_choices(self) -> None:
    skill = self.read_skill("build-resume-portfolio-site")
    self.assertIn("当前会话单 Agent", skill)
    self.assertIn("多 Agent 并行", skill)
    self.assertIn("请明确选择 1 或 2", skill)
    self.assertIn("implementation_strategy_waiting_confirmation", skill)
    self.assertNotIn("fresh-agent-sequential", skill)

def test_strategy_recommendation_uses_actual_plan_characteristics(self) -> None:
    contract = self.read_site_reference("site-planning-contract.md")
    for marker in (
        "exact file scope",
        "dependencies",
        "coordination cost",
        "parallel speedup cannot be demonstrated",
        "recommend `当前会话单 Agent`",
    ):
        self.assertIn(marker, contract)

def test_strategy_selection_cannot_be_inferred_from_prior_approval(self) -> None:
    workflow = self.read_site_reference("workflow-contract.md")
    self.assertIn("todo_plan_waiting_confirmation --approve-->", workflow)
    self.assertIn("implementation_strategy_waiting_confirmation", workflow)
    self.assertIn("silence", workflow.lower())
    self.assertIn("prior approval", workflow.lower())
    self.assertIn("do not spawn", workflow.lower())

def test_category_preview_offer_precedes_user_selection(self) -> None:
    contract = self.read_site_reference("site-brainstorming-contract.md").lower()
    preview_offer = contract.index("ask whether to open the browser comparison")
    user_selection = contract.index("receive the user's selection")
    self.assertLess(preview_offer, user_selection)

    preview = self.read_site_reference("visual-style-preview-contract.md").lower()
    self.assertIn("before the user selects", preview)
    self.assertIn("agent's recommendation", preview)
    self.assertNotIn("after tentative selection", preview)
    self.assertNotIn("visual mark on the tentative selection", preview)
```

- [ ] **Step 2: Replace the packaged-workflow strategy assertion**

In `test_installed_skill_workflow.py`, replace any expectation for
`fresh-agent-sequential` with:

```python
def test_workflow_requires_an_explicit_two_choice_strategy_gate(self) -> None:
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    for marker in (
        "当前会话单 Agent",
        "多 Agent 并行",
        "implementation_strategy_waiting_confirmation",
        "请明确选择 1 或 2",
    ):
        self.assertIn(marker, text)
    self.assertNotIn("fresh-agent-sequential", text)
```

In `test_synced_workflow_baseline.py`, replace
`self.assertIn("fresh-agent-sequential", text)` with:

```python
self.assertIn("当前会话单 Agent", text)
self.assertIn("多 Agent 并行", text)
self.assertNotIn("fresh-agent-sequential", text)
```

- [ ] **Step 3: Run focused tests and verify RED**

Run:

```powershell
python -m unittest tests.test_workflow_behavior_contract.WorkflowBehaviorContractTests.test_strategy_gate_offers_exactly_two_explicit_choices -v
python -m unittest tests.test_workflow_behavior_contract.WorkflowBehaviorContractTests.test_strategy_recommendation_uses_actual_plan_characteristics -v
python -m unittest tests.test_workflow_behavior_contract.WorkflowBehaviorContractTests.test_strategy_selection_cannot_be_inferred_from_prior_approval -v
python -m unittest tests.test_workflow_behavior_contract.WorkflowBehaviorContractTests.test_category_preview_offer_precedes_user_selection -v
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_installed_skill_workflow.py" -v
```

Expected: the new assertions FAIL because the current Skill still lists three
strategies, has no explicit strategy waiting gate, and offers browser preview
after tentative selection.

- [ ] **Step 4: Commit the red tests**

```powershell
git add -- tests/test_workflow_behavior_contract.py skills/build-resume-portfolio-site/scripts/test_installed_skill_workflow.py skills/build-resume-portfolio-site/scripts/test_synced_workflow_baseline.py
git commit -m "test: define explicit portfolio strategy choice"
```

### Task 2: Require conversational strategy evidence in the machine plan

**Files:**
- Modify: `skills/build-resume-portfolio-site/references/site-implementation-plan-schema.json`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_site_implementation_plan.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_validate_site_implementation_plan.py`
- Modify: `tests/fixtures/site-plan-valid.json`
- Modify: `tests/test_workflow_behavior_contract.py`

**Interfaces:**
- Consumes: schema-version-2 plan with approved TODO tasks and exact files.
- Produces: required `strategy_selection` object whose selected value matches `strategy`; accepted strategies are only `single-agent` and `parallel-wave`.

- [ ] **Step 1: Add strategy-selection fields to valid test data**

Add this object after `generation_mode` in both `valid_plan()` and
`tests/fixtures/site-plan-valid.json`:

```json
"strategy_selection": {
  "status": "user_selected",
  "source": "explicit_user",
  "channel": "conversation",
  "selected": "single-agent",
  "recommended": "single-agent",
  "reasons": ["Shared React and global-style files make coordination slower."]
}
```

- [ ] **Step 2: Add failing validator tests**

Add these tests to `SiteImplementationPlanValidatorTests`:

```python
def test_rejects_missing_explicit_strategy_selection(self) -> None:
    payload = valid_plan()
    payload.pop("strategy_selection")
    result = self.run_validator(payload)
    self.assertEqual(result.returncode, 1)
    self.assertIn("strategy_selection", result.stdout)

def test_rejects_browser_strategy_selection(self) -> None:
    payload = valid_plan()
    payload["strategy_selection"]["channel"] = "browser"
    result = self.run_validator(payload)
    self.assertEqual(result.returncode, 1)
    self.assertIn("explicit and conversational", result.stdout)

def test_rejects_strategy_that_differs_from_selection(self) -> None:
    payload = valid_plan()
    payload["strategy"] = "parallel-wave"
    result = self.run_validator(payload)
    self.assertEqual(result.returncode, 1)
    self.assertIn("must match", result.stdout)

def test_rejects_retired_sequential_strategy(self) -> None:
    payload = valid_plan()
    payload["strategy"] = "fresh-agent-sequential"
    payload["strategy_selection"]["selected"] = "fresh-agent-sequential"
    result = self.run_validator(payload)
    self.assertEqual(result.returncode, 1)
    self.assertIn("unsupported strategy", result.stdout)

def test_rejects_recommendation_without_reasons(self) -> None:
    payload = valid_plan()
    payload["strategy_selection"]["reasons"] = []
    result = self.run_validator(payload)
    self.assertEqual(result.returncode, 1)
    self.assertIn("recommendation reasons", result.stdout)
```

Update parallel mutations in existing tests so both
`payload["strategy"]` and `payload["strategy_selection"]["selected"]` become
`"parallel-wave"`.

- [ ] **Step 3: Run validator tests and verify RED**

Run:

```powershell
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_validate_site_implementation_plan.py" -v
```

Expected: new negative tests FAIL because `strategy_selection` is not required and `fresh-agent-sequential` is still accepted.

- [ ] **Step 4: Extend the JSON schema**

Add `strategy_selection` to `required`, reduce `strategy.enum` to
`["single-agent", "parallel-wave"]`, and add:

```json
"strategy_selection": {
  "type": "object",
  "additionalProperties": false,
  "required": ["status", "source", "channel", "selected", "recommended", "reasons"],
  "properties": {
    "status": {"const": "user_selected"},
    "source": {"const": "explicit_user"},
    "channel": {"const": "conversation"},
    "selected": {"enum": ["single-agent", "parallel-wave"]},
    "recommended": {"enum": ["single-agent", "parallel-wave"]},
    "reasons": {
      "type": "array",
      "minItems": 1,
      "items": {"type": "string", "minLength": 1}
    }
  }
}
```

- [ ] **Step 5: Implement minimal validator rules**

Change the constant and required fields:

```python
STRATEGIES = {"single-agent", "parallel-wave"}

REQUIRED = {
    # existing fields...
    "strategy_selection",
}
```

After validating `generation_mode`, add:

```python
selection = payload["strategy_selection"]
if not isinstance(selection, dict):
    errors.append("strategy selection must be recorded")
else:
    conversational = (
        selection.get("status") == "user_selected"
        and selection.get("source") == "explicit_user"
        and selection.get("channel") == "conversation"
    )
    if not conversational:
        errors.append("strategy selection must be explicit and conversational")
    if selection.get("selected") != payload["strategy"]:
        errors.append("strategy must match the explicit strategy selection")
    if selection.get("recommended") not in STRATEGIES:
        errors.append("recommended strategy is unsupported")
    if not _strings(selection.get("reasons"), non_empty=True):
        errors.append("strategy recommendation reasons must be non-empty")
```

Set multi-Agent detection to:

```python
multi_agent = payload["strategy"] == "parallel-wave"
```

- [ ] **Step 6: Update repository fixture mutations**

In `test_overlapping_parallel_ownership_is_rejected`, set:

```python
payload["strategy"] = "parallel-wave"
payload["strategy_selection"]["selected"] = "parallel-wave"
payload["multi_agent_authorized"] = True
```

- [ ] **Step 7: Run focused validators and verify GREEN**

Run:

```powershell
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_validate_site_implementation_plan.py" -v
python -m unittest tests.test_workflow_behavior_contract.WorkflowBehaviorContractTests.test_valid_full_workflow_artifacts_pass -v
python -m unittest tests.test_workflow_behavior_contract.WorkflowBehaviorContractTests.test_overlapping_parallel_ownership_is_rejected -v
```

Expected: all focused tests PASS.

- [ ] **Step 8: Commit plan validation**

```powershell
git add -- skills/build-resume-portfolio-site/references/site-implementation-plan-schema.json skills/build-resume-portfolio-site/scripts/validate_site_implementation_plan.py skills/build-resume-portfolio-site/scripts/test_validate_site_implementation_plan.py tests/fixtures/site-plan-valid.json tests/test_workflow_behavior_contract.py
git commit -m "feat: require explicit portfolio strategy selection"
```

### Task 3: Restrict multi-Agent planning to parallel execution

**Files:**
- Modify: `skills/build-resume-portfolio-site/references/multi-agent-implementation-schema.json`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_multi_agent_plan.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_validate_multi_agent_plan.py`
- Modify: `skills/build-resume-portfolio-site/references/multi-agent-implementation-contract.md`

**Interfaces:**
- Consumes: explicit user selection of `parallel-wave` and approved TODO/file scope.
- Produces: a parallel-only multi-Agent schema and validator; sequential integration and review waves remain permitted inside the parallel strategy.

- [ ] **Step 1: Add a failing retired-strategy test**

Add to `MultiAgentPlanValidatorTests`:

```python
def test_rejects_retired_fresh_agent_sequential_strategy(self) -> None:
    plan = valid_plan()
    plan["strategy"] = "fresh-agent-sequential"
    plan["waves"] = [
        {"id": "wave-1", "mode": "sequential", "task_ids": ["hero"]},
        {"id": "wave-2", "mode": "sequential", "task_ids": ["gallery"]},
        {"id": "wave-3", "mode": "sequential", "task_ids": ["integration"]},
        {"id": "wave-4", "mode": "sequential", "task_ids": ["spec-review"]},
        {"id": "wave-5", "mode": "sequential", "task_ids": ["quality-review"]},
    ]
    result = self.run_validator(plan)
    self.assertEqual(result.returncode, 1)
    self.assertIn("strategy must be parallel-wave", result.stdout)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_validate_multi_agent_plan.py" -v
```

Expected: FAIL because the validator currently accepts a sequential strategy with sequential waves.

- [ ] **Step 3: Make the schema and validator parallel-only**

In the JSON schema, replace the strategy enum with:

```json
"strategy": {"const": "parallel-wave"}
```

In the validator, use:

```python
STRATEGIES = {"parallel-wave"}
```

Replace the strategy error with:

```python
if plan["strategy"] != "parallel-wave":
    errors.append("strategy must be parallel-wave")
```

Delete the `fresh-agent-sequential` conditional at the end. Keep the rule that
`parallel-wave` requires at least one parallel wave; sequential integration and
review waves remain valid.

- [ ] **Step 4: Rewrite the active multi-Agent contract**

Make the contract state:

```markdown
The only multi-Agent strategy is `parallel-wave`. Use it only after the user
explicitly selects `多 Agent 并行` and both plans validate. Require at least two
independently useful tasks in a parallel wave with disjoint write ownership.
Sequential waves may be used only for integration and dependent review inside
the selected parallel strategy; they are not a separate user-facing mode.
```

Retain existing main-Agent ownership, shared-file protection, task-report,
review, audit, and failure semantics.

- [ ] **Step 5: Run multi-Agent tests and verify GREEN**

Run:

```powershell
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_validate_multi_agent_plan.py" -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit parallel-only planning**

```powershell
git add -- skills/build-resume-portfolio-site/references/multi-agent-implementation-schema.json skills/build-resume-portfolio-site/scripts/validate_multi_agent_plan.py skills/build-resume-portfolio-site/scripts/test_validate_multi_agent_plan.py skills/build-resume-portfolio-site/references/multi-agent-implementation-contract.md
git commit -m "feat: restrict portfolio multi-agent work to parallel waves"
```

### Task 4: Implement the explicit recommendation and selection gate

**Files:**
- Modify: `skills/build-resume-portfolio-site/SKILL.md`
- Modify: `skills/build-resume-portfolio-site/references/workflow-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/site-planning-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/artifact-layout.md`
- Modify: `skills/build-resume-portfolio-site/references/site-brainstorming-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/visual-style-preview-contract.md`
- Modify if stale: `skills/build-resume-portfolio-site/agents/openai.yaml`

**Interfaces:**
- Consumes: approved content and candidates during discovery, then an approved schema-v3 design specification and explicitly approved readable TODO plan.
- Produces: preview-before-selection category transactions, `implementation_strategy_waiting_confirmation`, exact recommendation output, explicit selection evidence, then a validated schema-v2 machine plan.

- [ ] **Step 1: Move every category preview offer before user selection**

In `SKILL.md`, `site-brainstorming-contract.md`, and
`visual-style-preview-contract.md`, use this order:

```markdown
1. Compare candidates and recommend one with fit, risk, and trade-offs.
2. Ask separately whether to open the browser comparison for this category.
3. On acceptance, show all candidates in an independent display-only Gallery;
   on decline, record the decline and continue text-only.
4. Receive the user's selection in the conversation.
5. Receive explicit confirmation, revision, or rejection, then lock the category.
```

Change Gallery output from “a visual mark on the tentative selection” to “a
visual mark on the Agent's recommendation with no interaction semantics.” Keep
browser activity non-authoritative and consent category-specific. For explicitly
skipped media, record the reason and do not offer a media preview.

- [ ] **Step 2: Rewrite the TODO-to-machine-plan sequence in `SKILL.md`**

After TODO approval, require the Agent to:

```markdown
5. Evaluate the approved TODO tasks, exact file scope, dependencies, shared-file
   coupling, independently useful tasks, and expected coordination cost.
6. Recommend one mode. If parallel speedup cannot be demonstrated, recommend
   `当前会话单 Agent`.
7. Present exactly:

   > 执行方式推荐：<当前会话单 Agent | 多 Agent 并行>
   >
   > 原因：<plan-specific reasons and speed/coordination trade-off>
   >
   > 1. 当前会话单 Agent
   > 2. 多 Agent 并行
   >
   > 请明确选择 1 或 2。

8. Set `stage=implementation_strategy_waiting_confirmation`. Wait for an
   explicit conversational `1` or `2`; prior approval, silence, browser
   activity, or inferred preference cannot select a mode.
9. Write `strategy_selection` and the selected strategy into the machine plan,
   then validate it. Do not edit React source or spawn agents before validation.
```

Replace the old three-strategy section. For parallel choice, require the
separate parallel plan and its validator. For an unsafe parallel choice, show
the exact conflicting files/dependencies and wait for a revised plan or a new
explicit selection; do not silently fall back.

- [ ] **Step 3: Update the workflow state machine**

Use these transitions in `workflow-contract.md`:

```text
todo_plan_waiting_confirmation --approve--> implementation_strategy_waiting_confirmation
implementation_strategy_waiting_confirmation --choose 1--> implementation_plan_generating
implementation_strategy_waiting_confirmation --choose 2--> implementation_plan_generating
implementation_strategy_waiting_confirmation --choose 2 and unsafe--> implementation_strategy_waiting_confirmation
implementation_plan_generating --plan validates--> integrated_generating
```

State that no earlier approval supplies strategy authorization and no Agent is
spawned while waiting.

- [ ] **Step 4: Update planning and artifact contracts**

In `site-planning-contract.md`, place strategy recommendation and explicit
selection after readable TODO approval and before machine-plan creation. Include
all recommendation predicates from the design specification and document the
required `strategy_selection` evidence.

In `artifact-layout.md`, describe `site-implementation-plan.json` as containing
the recommendation, reasons, explicit conversational selection, selected
strategy, exact tasks, and validation evidence. Describe
`multi-agent-implementation.json` as parallel-only.

- [ ] **Step 5: Check UI metadata for staleness**

Read `agents/openai.yaml`. If its short description still accurately describes
the Skill without promising a different strategy flow, leave it unchanged. If
it describes automatic or three-mode execution, regenerate only
`short_description` to mention explicit execution-mode choice.

- [ ] **Step 6: Run the behavior tests and verify GREEN**

Run:

```powershell
python -m unittest tests.test_workflow_behavior_contract -v
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_installed_skill_workflow.py" -v
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_synced_workflow_baseline.py" -v
```

Expected: all strategy-gate behavior tests PASS.

- [ ] **Step 7: Search active package resources for stale strategy vocabulary and preview ordering**

Run:

```powershell
Get-ChildItem skills/build-resume-portfolio-site -Recurse -File -Exclude *.pyc |
  Select-String -Pattern "fresh-agent-sequential|after tentative selection|visual mark on the tentative selection|three strateg|three execution|自动启动多 Agent"
```

Expected: active runtime contracts, schemas, validators, and fixtures contain no
`fresh-agent-sequential` or post-selection preview instructions. Test files may
contain only negative rejection or absence assertions. Historical repository
specs/plans outside the Skill package may retain them as history.

- [ ] **Step 8: Commit the runtime gate**

```powershell
git add -- skills/build-resume-portfolio-site/SKILL.md skills/build-resume-portfolio-site/references/workflow-contract.md skills/build-resume-portfolio-site/references/site-planning-contract.md skills/build-resume-portfolio-site/references/artifact-layout.md skills/build-resume-portfolio-site/references/site-brainstorming-contract.md skills/build-resume-portfolio-site/references/visual-style-preview-contract.md skills/build-resume-portfolio-site/agents/openai.yaml
git commit -m "feat: ask users to choose portfolio execution mode"
```

If `agents/openai.yaml` is unchanged, omit it from `git add`.

### Task 5: Verify, synchronize, and update the Draft PR

**Files:**
- Synchronize: `skills/build-resume-portfolio-site/` to `C:/Users/86135/.codex/skills/build-resume-portfolio-site/`
- No generated `.resume-site-work`, cache, or temporary files are committed.

**Interfaces:**
- Consumes: verified source Skill at branch HEAD.
- Produces: identical installed Skill package and updated Draft PR #2.

- [ ] **Step 1: Run the complete source test matrix**

Run:

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_*.py" -v
node --check skills/build-resume-portfolio-site/scripts/visual_companion/server.cjs
node --check skills/build-resume-portfolio-site/scripts/visual_companion/launch.cjs
node --check skills/build-resume-portfolio-site/scripts/visual_companion/stop.cjs
```

Expected: all Python tests PASS and all Node syntax checks exit `0`.

- [ ] **Step 2: Validate source resources and Skill structure**

Run:

```powershell
$env:PYTHONUTF8=1
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --stage discovery
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --stage planning
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --stage integrated
python C:/Users/86135/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/build-resume-portfolio-site
```

Expected: all resource reports have `"ok": true` and `"ready": true`; quick
validation prints `Skill is valid!`.

- [ ] **Step 3: Synchronize only the verified Skill package**

After filesystem approval, copy source package contents to
`C:/Users/86135/.codex/skills/build-resume-portfolio-site/`. Exclude
`__pycache__`, `*.pyc`, generated sessions, and temporary files. Do not touch
other installed Skills.

- [ ] **Step 4: Verify installed parity and runtime**

Compare source and installed relative file paths plus SHA-256 hashes. Expected:
equal file counts, no missing/extra paths, and zero hash differences.

Then run installed quick validation, discovery/planning/integrated resource
validation, and the installed script tests with `PYTHONDONTWRITEBYTECODE=1`.
Repository-only plugin metadata checks may skip in a standalone installation;
all executable and workflow tests must pass.

- [ ] **Step 5: Inspect final Git scope**

Run:

```powershell
git status -sb
git diff --check master...HEAD
git log --oneline master..HEAD
```

Expected: clean worktree, no whitespace errors, and only approved strategy-gate
changes plus their specs, plans, tests, and compatibility updates.

- [ ] **Step 6: Push and update Draft PR #2**

Push `codex/portable-visual-companion`. Update Draft PR #2 to mention the exact
two execution choices, plan-based recommendation, explicit conversational gate,
parallel-only multi-Agent validation, and test evidence. Verify it remains open,
Draft, based on `master`, and points to the local HEAD.

## Final verification checklist

- [ ] Every enabled visual category offers its independent browser comparison before user selection.
- [ ] A pre-selection Gallery marks only the Agent recommendation, never a nonexistent user selection.
- [ ] Exactly two execution modes are presented after TODO approval.
- [ ] The recommendation cites observable task, file, dependency, and coordination facts.
- [ ] Missing or ambiguous selection blocks machine-plan creation and implementation.
- [ ] `strategy_selection` proves explicit conversational choice and matches `strategy`.
- [ ] `fresh-agent-sequential` is rejected by both implementation-plan validators.
- [ ] Unsafe parallel work is blocked without automatic fallback.
- [ ] Main-Agent shared-file and integration ownership remains intact.
- [ ] Source and installed packages match by file set and SHA-256.
- [ ] Full Python, Node, resource, and quick-validation suites pass.
