# Superpowers-Style Workflow Internalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `subagent-driven-development` (recommended) or `executing-plans` to implement
> this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Internalize brainstorming, design approval, implementation planning,
fast-change routing, and safe agent-strategy selection into all relevant
skills in the `resume-portfolio-workflow` plugin.

**Architecture:** Add a thin orchestration skill and keep the two domain skills
independently safe. Each domain skill owns its discovery/planning contracts,
schemas, validators, and tests. The plugin first synchronizes its website skill
with the newer installed baseline, then adds schema-version-4 state migration
and packaging verification.

**Tech Stack:** Markdown Agent Skills, JSON contracts, Python 3 standard
library validators, `unittest`, Codex plugin manifest, Git, PowerShell ZIP
packaging.

## Global Constraints

- Do not require any external Superpowers skill at runtime.
- New content packages and new/structural site work use the full workflow.
- Existing confirmed artifacts may use the fast-change workflow only for
  bounded non-strategic changes.
- Ask one decision-bearing question at a time.
- Full discovery compares two or three materially different approaches.
- Never infer approval from silence or previous approval.
- Content design approval never equals final copy approval.
- No React source edits before website design approval and plan validation.
- Preserve user facts, confirmed snapshots, previews, and provenance.
- Multi-agent implementation requires explicit user authorization.
- Do not publish secrets, `.env`, caches, generated sites, or user materials.

---

### Task 1: Synchronize the Plugin Website Skill With the Newer Installed Baseline

**Files:**

- Create:
  `skills/build-resume-portfolio-site/scripts/test_synced_workflow_baseline.py`
- Replace from the installed source:
  `skills/build-resume-portfolio-site/SKILL.md`
- Create from the installed source:
  `skills/build-resume-portfolio-site/references/content-preflight-routing-contract.md`
- Create from the installed source:
  `skills/build-resume-portfolio-site/references/creative-direction-contract.md`
- Create from the installed source:
  `skills/build-resume-portfolio-site/references/creative-direction-schema.json`
- Create from the installed source:
  `skills/build-resume-portfolio-site/references/multi-agent-implementation-contract.md`
- Create from the installed source:
  `skills/build-resume-portfolio-site/references/multi-agent-implementation-schema.json`
- Create from the installed source:
  `skills/build-resume-portfolio-site/scripts/validate_content_handoff.py`
- Create from the installed source:
  `skills/build-resume-portfolio-site/scripts/validate_creative_direction.py`
- Create from the installed source:
  `skills/build-resume-portfolio-site/scripts/validate_multi_agent_plan.py`
- Create from the installed source:
  `skills/build-resume-portfolio-site/scripts/test_validate_content_handoff.py`
- Create from the installed source:
  `skills/build-resume-portfolio-site/scripts/test_validate_creative_direction.py`
- Create from the installed source:
  `skills/build-resume-portfolio-site/scripts/test_validate_multi_agent_plan.py`
- Modify only when the installed source differs:
  `skills/build-resume-portfolio-site/references/workflow-contract.md`
- Modify only when the installed source differs:
  `skills/build-resume-portfolio-site/references/artifact-layout.md`
- Modify only when the installed source differs:
  `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`
- Modify only when the installed source differs:
  `skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py`

**Interfaces:**

- Consumes: the installed baseline at
  `C:\Users\86135\.codex\skills\build-resume-portfolio-site`.
- Produces: a plugin-local website skill with content preflight, creative
  direction, and validated multi-agent planning.

- [ ] **Step 1: Write the failing synchronization test**

```python
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SyncedWorkflowBaselineTests(unittest.TestCase):
    def test_required_newer_baseline_resources_exist(self) -> None:
        required = [
            "references/content-preflight-routing-contract.md",
            "references/creative-direction-contract.md",
            "references/creative-direction-schema.json",
            "references/multi-agent-implementation-contract.md",
            "references/multi-agent-implementation-schema.json",
            "scripts/validate_content_handoff.py",
            "scripts/validate_creative_direction.py",
            "scripts/validate_multi_agent_plan.py",
        ]
        missing = [path for path in required if not (ROOT / path).is_file()]
        self.assertEqual(missing, [])

    def test_skill_routes_content_and_selects_agent_strategy(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("resume-content-intelligence", text)
        self.assertIn("fresh-agent-sequential", text)
        self.assertIn("parallel-wave", text)
        self.assertIn("creative-direction.json", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
python skills/build-resume-portfolio-site/scripts/test_synced_workflow_baseline.py
```

Expected: FAIL listing the newer baseline resources absent from the plugin.

- [ ] **Step 3: Copy only the newer baseline files**

Use `Copy-Item` with the exact source and destination paths listed above.
Do not copy `__pycache__`, local state, or unrelated files. Compare existing
shared files before replacing them.

- [ ] **Step 4: Run focused baseline tests**

Run:

```powershell
python skills/build-resume-portfolio-site/scripts/test_synced_workflow_baseline.py
python skills/build-resume-portfolio-site/scripts/test_validate_content_handoff.py
python skills/build-resume-portfolio-site/scripts/test_validate_creative_direction.py
python skills/build-resume-portfolio-site/scripts/test_validate_multi_agent_plan.py
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add -- skills/build-resume-portfolio-site
git commit -m "sync current portfolio workflow baseline"
```

---

### Task 2: Add the Plugin-Level Orchestration Skill

**Files:**

- Create: `skills/resume-portfolio-workflow/SKILL.md`
- Create: `skills/resume-portfolio-workflow/agents/openai.yaml`
- Create: `skills/resume-portfolio-workflow/references/routing-contract.md`
- Create: `skills/resume-portfolio-workflow/scripts/validate_workflow_route.py`
- Create: `skills/resume-portfolio-workflow/scripts/test_validate_workflow_route.py`
- Modify: `.codex-plugin/plugin.json`
- Modify: `README.md`

**Interfaces:**

- Consumes: user request, content handoff status, existing build state, and
  confirmed-artifact presence.
- Produces: `content-full`, `site-full`, or `site-fast-change` route without
  editing content or React source.

- [ ] **Step 1: Write failing route-validator tests**

```python
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_workflow_route.py"


def valid_route() -> dict:
    return {
        "schema_version": 1,
        "route": "site-fast-change",
        "reason": "bounded copy correction on a confirmed site",
        "content_package_status": "ready",
        "confirmed_artifact": "versions/v4-motion",
        "strategic_scope_changed": False,
        "structural_scope_changed": False,
        "affected_files": ["src/content/hero.js"],
        "verification": ["npm run build"],
        "rollback_baseline": "versions/v4-motion",
    }


class WorkflowRouteValidatorTests(unittest.TestCase):
    def run_validator(self, payload: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "route.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_bounded_fast_change(self) -> None:
        self.assertEqual(self.run_validator(valid_route()).returncode, 0)

    def test_rejects_fast_change_without_confirmed_artifact(self) -> None:
        payload = valid_route()
        payload["confirmed_artifact"] = None
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_fast_change_for_structural_scope(self) -> None:
        payload = valid_route()
        payload["structural_scope_changed"] = True
        self.assertEqual(self.run_validator(payload).returncode, 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
python skills/resume-portfolio-workflow/scripts/test_validate_workflow_route.py
```

Expected: FAIL because the orchestrator and validator do not exist.

- [ ] **Step 3: Implement the route validator**

Implement `validate_workflow_route.py` with these exact rules:

```python
ROUTES = {"content-full", "site-full", "site-fast-change"}

def validate(payload: dict) -> list[str]:
    required = {
        "schema_version", "route", "reason", "content_package_status",
        "confirmed_artifact", "strategic_scope_changed",
        "structural_scope_changed", "affected_files", "verification",
        "rollback_baseline",
    }
    errors = [
        f"missing field: {name}"
        for name in sorted(required - set(payload))
    ]
    if errors:
        return errors
    if payload["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if payload["route"] not in ROUTES:
        errors.append("unsupported route")
    if payload["route"] == "site-fast-change":
        if not payload["confirmed_artifact"]:
            errors.append("fast change requires a confirmed artifact")
        if payload["strategic_scope_changed"]:
            errors.append("strategic changes require the full workflow")
        if payload["structural_scope_changed"]:
            errors.append("structural changes require the full workflow")
        if not payload["affected_files"] or not payload["verification"]:
            errors.append("fast change requires files and verification")
        if not payload["rollback_baseline"]:
            errors.append("fast change requires a rollback baseline")
    return errors
```

Add a standard argparse/JSON `main()` matching the existing validators.

- [ ] **Step 4: Write the orchestrator skill**

`SKILL.md` must state the observable routing predicates, require one question
at a time in full mode, route content work before site work, and explicitly
forbid React/content edits by the orchestrator.

`routing-contract.md` must define:

```text
new/changed facts or copy -> content-full
ready content + new/structural/strategic site -> site-full
confirmed site + bounded local non-strategic edit -> site-fast-change
```

- [ ] **Step 5: Update plugin discovery metadata**

Set plugin version to `1.1.0`, mention all three skill names, and add a default
prompt that starts the complete content-to-site workflow.

- [ ] **Step 6: Run tests and plugin validation**

```powershell
python skills/resume-portfolio-workflow/scripts/test_validate_workflow_route.py
python C:\Users\86135\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py .
```

Expected: PASS and `Plugin validation passed`.

- [ ] **Step 7: Commit**

```powershell
git add -- .codex-plugin/plugin.json README.md skills/resume-portfolio-workflow
git commit -m "add resume portfolio workflow orchestrator"
```

---

### Task 3: Internalize Discovery and Planning in the Content Skill

**Files:**

- Create:
  `skills/resume-content-intelligence/references/content-brainstorming-contract.md`
- Create:
  `skills/resume-content-intelligence/references/content-planning-contract.md`
- Create:
  `skills/resume-content-intelligence/references/content-design-spec-schema.json`
- Create:
  `skills/resume-content-intelligence/references/content-implementation-plan-schema.json`
- Create:
  `skills/resume-content-intelligence/scripts/validate_content_design_spec.py`
- Create:
  `skills/resume-content-intelligence/scripts/validate_content_implementation_plan.py`
- Create:
  `skills/resume-content-intelligence/scripts/test_validate_content_design_spec.py`
- Create:
  `skills/resume-content-intelligence/scripts/test_validate_content_implementation_plan.py`
- Modify: `skills/resume-content-intelligence/SKILL.md`
- Modify:
  `skills/resume-content-intelligence/references/content-package-contract.md`
- Modify:
  `skills/resume-content-intelligence/references/conversation-workflow.md`

**Interfaces:**

- Consumes: source inventory, fact/evidence IDs, target role/JD, and explicit
  user answers.
- Produces: approved `content-design-spec.json`, validated
  `content-implementation-plan.json`, then the existing content package.

- [ ] **Step 1: Write failing design-spec tests**

Create a valid fixture with:

```python
{
    "schema_version": 1,
    "spec_id": "content-spec-1",
    "workflow_mode": "full",
    "inventory_complete": True,
    "target_audience": "frontend hiring team",
    "fixed_facts": ["fact-1"],
    "open_questions": [],
    "alternatives": [
        {"id": "evidence-first", "thesis": "Lead with verified outcomes",
         "tradeoffs": ["less personal narrative"]},
        {"id": "project-first", "thesis": "Lead with technical projects",
         "tradeoffs": ["work history appears later"]},
    ],
    "selected_alternative_id": "evidence-first",
    "decision_rationale": "Matches the target role and strongest evidence.",
    "approval": {"status": "user_approved", "source": "explicit_user"},
}
```

Tests must reject:

- fewer than two alternatives in full mode;
- a selected ID absent from alternatives;
- `approval.status` other than `user_approved`;
- facts not represented as stable non-empty IDs;
- `TODO` or `TBD` in any string field.

- [ ] **Step 2: Run design-spec tests and verify RED**

```powershell
python skills/resume-content-intelligence/scripts/test_validate_content_design_spec.py
```

Expected: FAIL because the validator does not exist.

- [ ] **Step 3: Implement the content design contract and validator**

The validator must expose `validate(payload) -> list[str]`, use only the Python
standard library, print stable `ERROR:` lines on exit `1`, and print
`OK: content design spec is valid` on exit `0`.

- [ ] **Step 4: Write failing implementation-plan tests**

The valid plan fixture must contain:

```python
{
    "schema_version": 1,
    "design_spec_id": "content-spec-1",
    "tasks": [{
        "id": "rewrite-project-1",
        "fact_ids": ["fact-1"],
        "evidence_ids": ["evidence-1"],
        "target_files": [".resume-site-work/input/approved-copy.json"],
        "produces": ["approved_copy.project-1"],
        "blocked_claims": [],
        "verification": [
            "python validate_content_package.py package.json"
        ],
    }],
    "handoff_criteria": [
        "All visible claims cite facts or explicit confirmation."
    ],
}
```

Tests must reject empty tasks, missing exact target files, unsupported claims
without evidence/confirmation, placeholder strings, and missing handoff
criteria.

- [ ] **Step 5: Implement the content plan contract and validator**

Use the same CLI and stable exit-code pattern as the design validator.

- [ ] **Step 6: Update content workflow instructions**

Place the new sequence before copy optimization:

```text
inventory -> one-question dialogue -> 2-3 strategies -> explicit strategy
approval -> validated implementation plan -> copy drafting -> final copy
approval -> content package handoff
```

State explicitly that strategy approval does not approve final copy and that
fast change is allowed only for a bounded revision to an existing approved
content package.

- [ ] **Step 7: Run focused content tests**

```powershell
python skills/resume-content-intelligence/scripts/test_validate_content_design_spec.py
python skills/resume-content-intelligence/scripts/test_validate_content_implementation_plan.py
python -m unittest discover -s skills/resume-content-intelligence/scripts -p "test_*.py"
```

Expected: all focused tests PASS.

- [ ] **Step 8: Commit**

```powershell
git add -- skills/resume-content-intelligence
git commit -m "internalize content discovery and planning"
```

---

### Task 4: Internalize Discovery and File-Level Planning in the Website Skill

**Files:**

- Create:
  `skills/build-resume-portfolio-site/references/site-brainstorming-contract.md`
- Create:
  `skills/build-resume-portfolio-site/references/site-planning-contract.md`
- Create:
  `skills/build-resume-portfolio-site/references/site-design-spec-schema.json`
- Create:
  `skills/build-resume-portfolio-site/references/site-implementation-plan-schema.json`
- Create:
  `skills/build-resume-portfolio-site/scripts/validate_site_design_spec.py`
- Create:
  `skills/build-resume-portfolio-site/scripts/validate_site_implementation_plan.py`
- Create:
  `skills/build-resume-portfolio-site/scripts/test_validate_site_design_spec.py`
- Create:
  `skills/build-resume-portfolio-site/scripts/test_validate_site_implementation_plan.py`
- Modify: `skills/build-resume-portfolio-site/SKILL.md`
- Modify:
  `skills/build-resume-portfolio-site/references/creative-direction-contract.md`
- Modify:
  `skills/build-resume-portfolio-site/references/artifact-layout.md`
- Modify:
  `skills/build-resume-portfolio-site/references/workflow-contract.md`
- Modify:
  `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`
- Modify:
  `skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py`

**Interfaces:**

- Consumes: validated content package, authorized media, references, existing
  build state, and explicit user design decisions.
- Produces: approved `site-design-spec.json`, validated
  `site-implementation-plan.json`, and inputs for `creative-direction.json`.

- [ ] **Step 1: Write failing site-design tests**

The valid full-mode fixture must include:

```python
{
    "schema_version": 1,
    "spec_id": "site-spec-1",
    "workflow_mode": "full",
    "content_revision": 1,
    "visual_protagonist": "project outcomes",
    "fixed_constraints": ["preserve approved copy"],
    "open_ceiling": ["composition", "motion language"],
    "avoid": ["generic card grid"],
    "alternatives": [
        {"id": "editorial", "family": "radical editorial",
         "tradeoffs": ["denser reading rhythm"]},
        {"id": "cinematic", "family": "cinematic portfolio",
         "tradeoffs": ["higher media dependency"]},
    ],
    "selected_alternative_id": "editorial",
    "composition_commitment": "asymmetric editorial stage",
    "type_color_character": "high-contrast serif and restrained yellow",
    "representative_interaction": "project selection updates one detail panel",
    "approval": {"status": "user_approved", "source": "explicit_user"},
}
```

Reject fewer than two full-mode alternatives, generic/duplicate alternatives,
unselected IDs, absent approval, empty visual protagonist, placeholders, and
contradictions between fixed and avoid lists.

- [ ] **Step 2: Run site-design tests and verify RED**

```powershell
python skills/build-resume-portfolio-site/scripts/test_validate_site_design_spec.py
```

Expected: FAIL because the validator does not exist.

- [ ] **Step 3: Implement the site design contract and validator**

Require explicit user approval before structural React edits. Define
`site-design-spec.json` as the approved product/experience decision and
`creative-direction.json` as its visual implementation translation.

- [ ] **Step 4: Write failing site-plan tests**

The valid single-agent fixture must include:

```python
{
    "schema_version": 1,
    "design_spec_id": "site-spec-1",
    "strategy": "single-agent",
    "tasks": [{
        "id": "prototype-shell",
        "depends_on": [],
        "files": ["src/App.jsx", "src/styles.css"],
        "consumes": ["approved-copy.json", "site-design-spec.json"],
        "produces": ["five-region prototype"],
        "acceptance": ["Representative interaction is rendered."],
        "verification": [
            "python validate_vite_project.py .resume-site-work/site --stage prototype",
            "npm run build"
        ],
    }],
    "rollback_baseline": "empty/new site",
    "snapshot_target": "versions/v1-prototype",
}
```

Reject missing files, dependencies on unknown task IDs, duplicate write
ownership in a parallel strategy, absent verification, placeholders, and
multi-agent strategies without explicit authorization plus a validated
`multi-agent-implementation.json` reference.

- [ ] **Step 5: Implement the site plan contract and validator**

Reuse the multi-agent validator's ownership concepts but keep the
site-implementation plan independently valid for `single-agent`.

- [ ] **Step 6: Update website workflow instructions**

Insert before Stage 1:

```text
route classification -> discovery -> one question at a time -> 2-3 layout
families -> site design approval -> site implementation plan -> implementation
strategy -> Stage 1
```

For fast changes, require a validated route report and bounded change brief;
do not regenerate the overall creative direction.

- [ ] **Step 7: Update resource validation**

Add `discovery` and `planning` resource groups to
`validate_skill_resources.py`. Tests must prove missing contracts return the
existing malformed/missing resource exit code.

- [ ] **Step 8: Run focused website tests**

```powershell
python skills/build-resume-portfolio-site/scripts/test_validate_site_design_spec.py
python skills/build-resume-portfolio-site/scripts/test_validate_site_implementation_plan.py
python skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py
python skills/build-resume-portfolio-site/scripts/test_validate_creative_direction.py
python skills/build-resume-portfolio-site/scripts/test_validate_multi_agent_plan.py
```

Expected: all tests PASS.

- [ ] **Step 9: Commit**

```powershell
git add -- skills/build-resume-portfolio-site
git commit -m "internalize site discovery and implementation planning"
```

---

### Task 5: Add Build-State Version 4 and Safe Version-3 Migration

**Files:**

- Create:
  `skills/build-resume-portfolio-site/scripts/migrate_build_state.py`
- Create:
  `skills/build-resume-portfolio-site/scripts/test_migrate_build_state.py`
- Modify:
  `skills/build-resume-portfolio-site/references/workflow-contract.md`
- Modify:
  `skills/build-resume-portfolio-site/references/artifact-layout.md`
- Modify: `skills/build-resume-portfolio-site/SKILL.md`

**Interfaces:**

- Consumes: schema-version-3 `build-state.json`.
- Produces: schema-version-4 state while preserving confirmed artifacts and
  deriving no new approval.

- [ ] **Step 1: Write failing migration tests**

Use this minimum version-3 fixture:

```python
{
    "schema_version": 3,
    "skill_version": "1.1.0-react-vite",
    "stage": "complete",
    "last_confirmed_artifact": "versions/v4-motion",
    "confirmations": {
        "prototype": True,
        "media_direction": True,
        "motion": True,
    },
    "current_artifact": "versions/v4-motion",
    "current_preview": "preview/dist/index.html",
    "attempted_direction_ids": ["editorial"],
    "attempted_media_direction_ids": [],
    "visual_repair_round": 0,
}
```

Verify migration:

- preserves every existing field and value except version metadata;
- sets `schema_version` to `4`;
- adds `workflow_mode: "fast-change-eligible"` only when a confirmed artifact
  exists;
- adds discovery/planning approvals as `False`;
- never changes existing prototype/media/motion confirmations;
- rejects version 2, malformed confirmations, and missing snapshot references
  when a confirmation is true;
- refuses to overwrite an existing output path.

- [ ] **Step 2: Run migration tests and verify RED**

```powershell
python skills/build-resume-portfolio-site/scripts/test_migrate_build_state.py
```

Expected: FAIL because the migration tool does not exist.

- [ ] **Step 3: Implement atomic migration**

Expose:

```python
def migrate(state: dict) -> dict:
    if state.get("schema_version") != 3:
        raise ValueError("only schema_version 3 can migrate to 4")
    migrated = dict(state)
    migrated["schema_version"] = 4
    migrated["skill_version"] = "1.2.0-react-vite"
    migrated["workflow_mode"] = (
        "fast-change-eligible"
        if state.get("last_confirmed_artifact")
        else "full"
    )
    migrated["discovery"] = {
        "site_design_approved": False,
        "site_plan_validated": False,
    }
    return migrated
```

The CLI writes to a distinct output path using a temporary sibling file and
atomic rename. It must never mutate the input file in place.

- [ ] **Step 4: Update contracts and startup routing**

Document version 4 as the only active state and allow explicit migration of
version 3 through the script. Existing confirmed version-3 sites may migrate
into fast-change eligibility without receiving new design approval.

- [ ] **Step 5: Run migration and workflow tests**

```powershell
python skills/build-resume-portfolio-site/scripts/test_migrate_build_state.py
python skills/build-resume-portfolio-site/scripts/test_installed_skill_workflow.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add -- skills/build-resume-portfolio-site
git commit -m "add safe workflow state migration"
```

---

### Task 6: Add Skill-Behavior Pressure Scenarios and Cross-Skill Regression Tests

**Files:**

- Create: `tests/test_workflow_behavior_contract.py`
- Create: `tests/fixtures/content-design-spec-valid.json`
- Create: `tests/fixtures/content-plan-valid.json`
- Create: `tests/fixtures/site-design-spec-valid.json`
- Create: `tests/fixtures/site-plan-valid.json`
- Create: `tests/fixtures/workflow-route-fast-valid.json`
- Create: `docs/superpowers/reports/2026-07-26-skill-behavior-verification.md`

**Interfaces:**

- Consumes: all three skill instructions and validators.
- Produces: repeatable evidence that full and fast workflows remain distinct.

- [ ] **Step 1: Encode cross-skill contract assertions**

```python
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WorkflowBehaviorContractTests(unittest.TestCase):
    def read_skill(self, name: str) -> str:
        return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")

    def test_all_three_skills_are_discoverable(self) -> None:
        for name in (
            "resume-portfolio-workflow",
            "resume-content-intelligence",
            "build-resume-portfolio-site",
        ):
            self.assertTrue((ROOT / "skills" / name / "SKILL.md").is_file())

    def test_domain_skills_do_not_require_external_superpowers(self) -> None:
        for name in ("resume-content-intelligence", "build-resume-portfolio-site"):
            text = self.read_skill(name)
            self.assertIn("one question at a time", text.lower())
            self.assertIn("implementation plan", text.lower())
            self.assertNotIn("REQUIRED SUB-SKILL: Use superpowers:", text)

    def test_site_skill_blocks_source_edits_before_approval(self) -> None:
        text = self.read_skill("build-resume-portfolio-site")
        self.assertIn("Do not edit React source before", text)
        self.assertIn("site-design-spec.json", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run contract tests**

```powershell
python tests/test_workflow_behavior_contract.py
```

Expected: PASS after Tasks 2–5.

- [ ] **Step 3: Run fresh-context pressure scenarios**

Record five scenarios in the report:

1. rushed new site;
2. unsupported resume metric;
3. vague redesign with collapsed alternatives;
4. overlapping multi-agent ownership;
5. bounded copy correction.

For each scenario, record expected route, gate, forbidden action, and observed
behavior. No user data or model chain-of-thought enters the report.

- [ ] **Step 4: Fix instruction gaps and rerun**

Only modify the smallest relevant contract or `SKILL.md`. Repeat the failing
scenario until observed behavior matches the expected route and gate.

- [ ] **Step 5: Commit**

```powershell
git add -- tests docs/superpowers/reports skills
git commit -m "verify internalized workflow behavior"
```

---

### Task 7: Validate, Package, Scan, and Publish the Plugin

**Files:**

- Modify: `README.md`
- Modify: `.codex-plugin/plugin.json`
- Create or replace: `D:\resume\resume-portfolio-workflow-plugin.zip`
- Create or replace: `D:\resume\resume-portfolio-skills.zip`

**Interfaces:**

- Consumes: validated plugin source at the current commit.
- Produces: public GitHub source and two inspected ZIP distributions.

- [ ] **Step 1: Run focused and aggregate tests**

```powershell
python -m unittest discover -s skills/resume-content-intelligence/scripts -p "test_*.py"
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_*.py"
python -m unittest discover -s skills/resume-portfolio-workflow/scripts -p "test_*.py"
python -m unittest discover -s tests -p "test_*.py"
```

Expected: all tests PASS.

- [ ] **Step 2: Validate the plugin**

```powershell
python C:\Users\86135\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py .
```

Expected: `Plugin validation passed`.

- [ ] **Step 3: Scan staged source for sensitive information**

Scan for:

```text
.env
gho_ tokens
sk- keys
private-key headers
APIHZ_ID values
APIHZ_KEY values
password assignments
absolute user-material paths
```

Environment-variable names and documented placeholders are allowed; actual
credential-like values are not.

- [ ] **Step 4: Build both ZIP variants**

Plugin ZIP contents:

```text
.codex-plugin/
skills/
README.md
.gitignore
```

Skills-only ZIP contents:

```text
skills/
```

Exclude `.git`, `.env*`, `__pycache__`, `.pytest_cache`, generated sites,
workspace state, and user media.

- [ ] **Step 5: Inspect ZIP entries**

Assert:

```text
plugin ZIP contains .codex-plugin/plugin.json
plugin ZIP contains all three SKILL.md files
skills ZIP contains all three SKILL.md files
neither ZIP contains .git or .env entries
```

- [ ] **Step 6: Review the final diff**

```powershell
git status --short --branch
git diff --check
git diff --stat origin/master...HEAD
```

Expected: no whitespace errors and no unrelated files.

- [ ] **Step 7: Commit packaging metadata**

Do not commit ZIP binaries unless explicitly requested. Commit source metadata:

```powershell
git add -- .codex-plugin/plugin.json README.md
git commit -m "prepare workflow plugin release"
```

Skip the commit if no source metadata changed.

- [ ] **Step 8: Push**

```powershell
git push origin master
```

Expected: remote branch points to the verified local commit.

## Plan Self-Review

- Spec coverage: all architecture, domain, routing, approval, migration,
  multi-agent, validation, packaging, and publication requirements map to a
  task.
- Placeholder scan: no unresolved placeholders or unspecified test steps are
  present. Literal `TODO` and `TBD` occurrences describe validator rejection
  cases.
- Interface consistency: report names and skill names match the approved
  design specification.
- Scope: each task produces an independently testable deliverable and keeps
  shared files in a single task.
