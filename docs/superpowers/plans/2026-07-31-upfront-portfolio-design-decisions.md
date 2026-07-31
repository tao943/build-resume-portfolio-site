# Upfront Portfolio Design Decisions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make full portfolio discovery confirm six independent design dimensions and a human-readable TODO plan before generating one integrated React + Vite website.

**Architecture:** Extend the existing display-only Visual Companion instead of adding browser-side interaction. Store six category decisions in site-design schema v3, require a separately approved Markdown TODO plan plus machine-validatable implementation plan, then replace the prototype/media/motion confirmation chain with one integrated generation transaction and a three-choice acceptance loop.

**Tech Stack:** Markdown Agent Skill contracts, JSON Schema draft 2020-12, Python 3 standard-library validators and `unittest`, Node.js Visual Companion scripts, React + Vite output validation.

## Global Constraints

- Browser previews are independent and display-only; browser activity never selects or approves anything.
- Full discovery order is structure, typography, color, conditional media, primary motion, secondary motion.
- Every enabled category receives a separate browser-preview offer after tentative selection.
- Media may be skipped only with an explicit reason.
- Exactly one primary-motion system is selected; secondary motion supports compatible multi-selection without a fixed numeric cap.
- Final requirements and the readable TODO plan both require explicit conversational approval before React source edits.
- The first React candidate integrates all confirmed decisions in one generation transaction.
- Responsive behavior, accessibility, coarse-pointer support, fallbacks, and reduced motion are mandatory engineering constraints.
- Fast-change remains available only for bounded edits to an existing confirmed artifact.
- Use the existing Node-only loopback Visual Companion; add no browser plugin, browser approval control, analytics, or runtime package dependency.
- Preserve approved resume facts and authorized-media boundaries.

---

## File map

- `tests/test_workflow_behavior_contract.py`: repository-level workflow assertions and validator integration coverage.
- `tests/fixtures/site-design-spec-valid.json`: canonical schema-v3 full-discovery artifact.
- `tests/fixtures/site-plan-valid.json`: canonical approved human/machine planning artifact.
- `skills/build-resume-portfolio-site/references/site-design-spec-schema.json`: machine-readable six-decision contract.
- `skills/build-resume-portfolio-site/scripts/validate_site_design_spec.py`: semantic validation beyond JSON Schema.
- `skills/build-resume-portfolio-site/scripts/test_validate_site_design_spec.py`: unit coverage for category order, preview response, skip, approval, and motion selection.
- `skills/build-resume-portfolio-site/references/site-implementation-plan-schema.json`: machine-readable plan approval contract.
- `skills/build-resume-portfolio-site/scripts/validate_site_implementation_plan.py`: semantic validation for readable-plan path and explicit approval.
- `skills/build-resume-portfolio-site/scripts/test_validate_site_implementation_plan.py`: plan-gate unit coverage.
- `skills/build-resume-portfolio-site/references/site-brainstorming-contract.md`: six-category discovery transaction.
- `skills/build-resume-portfolio-site/references/visual-style-preview-contract.md`: independent per-category Gallery rules.
- `skills/build-resume-portfolio-site/references/site-planning-contract.md`: synchronized Markdown/JSON plan and conversational approval.
- `skills/build-resume-portfolio-site/references/workflow-contract.md`: integrated state machine, rollback, and final acceptance loop.
- `skills/build-resume-portfolio-site/references/artifact-layout.md`: decision galleries, `site-todo-plan.md`, and integrated snapshots.
- `skills/build-resume-portfolio-site/prompts/01-generate-integrated-site.md`: one-pass implementation prompt that consumes all confirmed decisions.
- `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`: integrated-stage resource registration.
- `skills/build-resume-portfolio-site/scripts/validate_vite_project.py`: `integrated` stage validation.
- `skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py`: integrated resource discovery coverage.
- `skills/build-resume-portfolio-site/scripts/test_validate_vite_project.py`: integrated-stage quality and reduced-motion coverage.
- `skills/build-resume-portfolio-site/SKILL.md`: authoritative runtime orchestration.
- `README.md`: public workflow description.

### Task 1: Lock the new workflow behavior with failing contract tests

**Files:**
- Modify: `tests/test_workflow_behavior_contract.py`

**Interfaces:**
- Consumes: approved design specification `docs/superpowers/specs/2026-07-31-upfront-portfolio-design-decisions.md`.
- Produces: failing behavioral assertions that every later task must satisfy.

- [ ] **Step 1: Add the full-discovery sequence assertion**

Add a test that reads `site-brainstorming-contract.md`, finds these exact markers, and asserts their positions increase:

```python
def test_full_discovery_orders_six_independent_decisions(self) -> None:
    contract = self.read_site_reference("site-brainstorming-contract.md").lower()
    markers = (
        "overall structure",
        "typography",
        "color system",
        "media treatment",
        "primary motion",
        "secondary motion",
        "final requirements confirmation",
        "todo plan approval",
    )
    positions = [contract.index(marker) for marker in markers]
    self.assertEqual(positions, sorted(positions))
```

Add `read_site_reference()` beside `read_skill()` so reference lookup is not duplicated.

- [ ] **Step 2: Add independent preview and plan-gate assertions**

```python
def test_each_enabled_decision_gets_a_separate_preview_offer(self) -> None:
    contract = self.read_site_reference("visual-style-preview-contract.md").lower()
    self.assertIn("ask separately for every enabled category", contract)
    self.assertIn("independent, not cumulative", contract)
    self.assertIn("declining one category", contract)

def test_site_skill_requires_readable_plan_approval_before_source_edits(self) -> None:
    text = self.read_skill("build-resume-portfolio-site").lower()
    self.assertIn("site-todo-plan.md", text)
    self.assertIn("todo plan approval", text)
    self.assertIn("do not edit react source", text)
    self.assertIn("one integrated", text)
```

- [ ] **Step 3: Add final acceptance assertions**

Assert the Skill contains the exact choices `当前效果满意，完成`, `加强动效`, and `提出修改`, and that the workflow contract says motion enhancement preserves structure, typography, color, and media treatment.

- [ ] **Step 4: Run the new tests and verify RED**

Run:

```powershell
python -m unittest discover -s tests -p "test_workflow_behavior_contract.py" -v
```

Expected: FAIL because the current contracts contain one cumulative Gallery, staged prototype/media/motion confirmations, and no readable-plan approval gate.

- [ ] **Step 5: Commit the failing behavior contract**

```powershell
git add -- tests/test_workflow_behavior_contract.py
git commit -m "test: define upfront portfolio workflow"
```

### Task 2: Upgrade the site design specification to schema version 3

**Files:**
- Modify: `skills/build-resume-portfolio-site/references/site-design-spec-schema.json`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_site_design_spec.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_validate_site_design_spec.py`
- Modify: `tests/fixtures/site-design-spec-valid.json`

**Interfaces:**
- Consumes: six decision categories and conversational approvals.
- Produces: validated `reports/site-design-spec.json` with `decision_order`, `decisions`, `engineering_constraints`, and `requirements_approval`.

- [ ] **Step 1: Replace the unit-test fixture with the wished-for v3 payload**

Use this top-level shape in `valid_spec()` and the repository fixture:

```python
{
    "schema_version": 3,
    "spec_id": "site-spec-1",
    "workflow_mode": "full",
    "content_revision": 1,
    "decision_order": [
        "structure", "typography", "color", "media",
        "primary_motion", "secondary_motion",
    ],
    "decisions": {
        "structure": confirmed_single("editorial", "structure-1"),
        "typography": confirmed_single("editorial-serif", "typography-1"),
        "color": confirmed_single("ink-yellow", "color-1"),
        "media": skipped_media("no authorized media"),
        "primary_motion": confirmed_single("section-reveal", "primary-motion-1"),
        "secondary_motion": confirmed_multi(
            ["card-feedback", "text-reveal"], "secondary-motion-1"
        ),
    },
    "engineering_constraints": [
        "responsive", "accessible", "coarse-pointer",
        "reduced-motion", "media-fallbacks",
    ],
    "requirements_approval": {
        "status": "user_approved",
        "source": "explicit_user",
        "channel": "conversation",
    },
}
```

A confirmed decision contains `status`, two or more candidate objects, `recommended_candidate_id`, `tentative_selection_ids`, `selected_candidate_ids`, `preview`, and `approval`. Preview contains `offered: true`, `response: accepted|declined`, `delivery: local-gallery|static-fallback|not-requested`, and nullable `artifact`. Approval must be explicit and conversational.

- [ ] **Step 2: Add failing semantic tests**

Add one focused test for each rule:

```python
def test_rejects_wrong_decision_order(self) -> None:
    payload = valid_spec()
    payload["decision_order"][0:2] = ["typography", "structure"]
    self.assertEqual(self.run_validator(payload).returncode, 1)

def test_rejects_missing_preview_offer_for_enabled_category(self) -> None:
    payload = valid_spec()
    payload["decisions"]["color"]["preview"]["offered"] = False
    result = self.run_validator(payload)
    self.assertEqual(result.returncode, 1)
    self.assertIn("color preview must be offered", result.stdout)

def test_accepts_declined_preview_and_later_accepted_preview(self) -> None:
    payload = valid_spec()
    payload["decisions"]["structure"]["preview"] = {
        "offered": True,
        "response": "declined",
        "delivery": "not-requested",
        "artifact": None,
    }
    self.assertEqual(self.run_validator(payload).returncode, 0)

def test_rejects_media_skip_without_reason(self) -> None:
    payload = valid_spec()
    payload["decisions"]["media"].pop("skip_reason")
    self.assertEqual(self.run_validator(payload).returncode, 1)

def test_rejects_multiple_primary_motion_selections(self) -> None:
    payload = valid_spec()
    decision = payload["decisions"]["primary_motion"]
    decision["selected_candidate_ids"] = [
        decision["candidates"][0]["id"],
        decision["candidates"][1]["id"],
    ]
    self.assertEqual(self.run_validator(payload).returncode, 1)

def test_accepts_multiple_compatible_secondary_motion_selections(self) -> None:
    payload = valid_spec()
    decision = payload["decisions"]["secondary_motion"]
    decision["selected_candidate_ids"] = [
        candidate["id"] for candidate in decision["candidates"]
    ]
    self.assertEqual(self.run_validator(payload).returncode, 0)

def test_rejects_unapproved_final_requirements(self) -> None:
    payload = valid_spec()
    payload["requirements_approval"]["status"] = "pending"
    self.assertEqual(self.run_validator(payload).returncode, 1)

def test_rejects_browser_approval_channel(self) -> None:
    payload = valid_spec()
    payload["decisions"]["typography"]["approval"]["channel"] = "browser"
    self.assertEqual(self.run_validator(payload).returncode, 1)

def test_rejects_version_two_for_new_full_discovery(self) -> None:
    payload = valid_spec()
    payload["schema_version"] = 2
    result = self.run_validator(payload)
    self.assertEqual(result.returncode, 1)
    self.assertIn("schema_version must be 3", result.stdout)
```

- [ ] **Step 3: Run validator tests and verify RED**

Run:

```powershell
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_validate_site_design_spec.py" -v
```

Expected: FAIL because the validator requires schema version 2 and one `visual_preview` object.

- [ ] **Step 4: Implement reusable decision validation**

Replace `_validate_visual_preview()` with these interfaces:

```python
DECISION_ORDER = (
    "structure", "typography", "color", "media",
    "primary_motion", "secondary_motion",
)

def _validate_preview(preview: Any, category: str) -> list[str]:
    if not isinstance(preview, dict):
        return [f"{category} requires a preview record"]
    errors: list[str] = []
    if preview.get("offered") is not True:
        errors.append(f"{category} preview must be offered")
    response = preview.get("response")
    delivery = preview.get("delivery")
    artifact = preview.get("artifact")
    if response not in {"accepted", "declined"}:
        errors.append(f"{category} preview response is invalid")
    if delivery not in {
        "local-gallery", "static-fallback", "not-requested"
    }:
        errors.append(f"{category} preview delivery is invalid")
    if response == "declined":
        if delivery != "not-requested" or artifact is not None:
            errors.append(f"{category} declined preview must not have an artifact")
        return errors
    if delivery == "not-requested":
        errors.append(f"{category} accepted preview requires delivery")
    normalized = str(artifact or "").replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.parts[:3]
        != (".resume-site-work", "style-preview", "sessions")
        or path.parts[-1:] != ("gallery.html",)
    ):
        errors.append(f"{category} preview artifact must be a session gallery")
    return errors

def _validate_confirmed_decision(
    category: str, decision: Any, *, allow_multiple: bool
) -> list[str]:
    if not isinstance(decision, dict) or decision.get("status") != "confirmed":
        return [f"{category} must be confirmed"]
    errors: list[str] = []
    candidates = decision.get("candidates")
    if not isinstance(candidates, list) or len(candidates) < 2:
        return [f"{category} requires at least two candidates"]
    ids = [item.get("id") for item in candidates if isinstance(item, dict)]
    if len(ids) != len(candidates) or not all(
        isinstance(item, str) and item.strip() for item in ids
    ) or len(ids) != len(set(ids)):
        errors.append(f"{category} candidate IDs must be unique")
    candidate_ids = set(ids)
    if decision.get("recommended_candidate_id") not in candidate_ids:
        errors.append(f"{category} recommendation must reference a candidate")
    for field in ("tentative_selection_ids", "selected_candidate_ids"):
        selected = decision.get(field)
        if not isinstance(selected, list) or not selected:
            errors.append(f"{category} {field} must be non-empty")
            continue
        if not allow_multiple and len(selected) != 1:
            errors.append(f"{category} requires exactly one selected candidate")
        if not set(selected) <= candidate_ids:
            errors.append(f"{category} {field} must reference candidates")
    errors.extend(_validate_preview(decision.get("preview"), category))
    approval = decision.get("approval")
    if not isinstance(approval, dict) or approval.get("status") != "user_approved":
        errors.append(f"{category} requires explicit approval")
    elif approval.get("source") != "explicit_user" or approval.get("channel") != "conversation":
        errors.append(f"{category} approval must be explicit and conversational")
    return errors

def _validate_media_decision(decision: Any) -> list[str]:
    if isinstance(decision, dict) and decision.get("status") == "skipped":
        reason = decision.get("skip_reason")
        return [] if isinstance(reason, str) and reason.strip() else [
            "media skip requires a reason"
        ]
    return _validate_confirmed_decision("media", decision, allow_multiple=False)
```

Validate candidate uniqueness, selected IDs, separate preview offer, artifact containment below `.resume-site-work/style-preview/sessions/`, explicit conversation approval, single primary selection, multi secondary selection, skip reason, mandatory constraints, and final requirements approval. Return stable category-prefixed errors such as `primary_motion requires exactly one selected candidate`.

- [ ] **Step 5: Replace the JSON Schema with the same v3 contract**

Define `$defs.candidate`, `$defs.preview`, `$defs.approval`, `$defs.confirmedDecision`, `$defs.singleDecision`, and `$defs.skippedMedia`. Use `oneOf` for media confirmed/skipped and `maxItems: 1` only for the selected IDs of single-choice categories. Do not add a maximum to `secondary_motion.selected_candidate_ids`.

- [ ] **Step 6: Run unit and repository behavior tests**

Run:

```powershell
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_validate_site_design_spec.py" -v
python -m unittest discover -s tests -p "test_workflow_behavior_contract.py" -v
```

Expected: schema-validator tests PASS; workflow tests remain RED only for contracts and planning not yet changed.

- [ ] **Step 7: Commit schema v3**

```powershell
git add -- skills/build-resume-portfolio-site/references/site-design-spec-schema.json skills/build-resume-portfolio-site/scripts/validate_site_design_spec.py skills/build-resume-portfolio-site/scripts/test_validate_site_design_spec.py tests/fixtures/site-design-spec-valid.json
git commit -m "feat: validate six portfolio decisions"
```

### Task 3: Require an approved readable TODO plan

**Files:**
- Modify: `skills/build-resume-portfolio-site/references/site-implementation-plan-schema.json`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_site_implementation_plan.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_validate_site_implementation_plan.py`
- Modify: `tests/fixtures/site-plan-valid.json`

**Interfaces:**
- Consumes: approved schema-v3 `site-design-spec.json` and `.resume-site-work/reports/site-todo-plan.md`.
- Produces: schema-v2 `site-implementation-plan.json` proving the readable plan was shown and explicitly approved.

- [ ] **Step 1: Add v2 plan fields to the wished-for fixture**

```json
{
  "schema_version": 2,
  "design_spec_id": "site-spec-1",
  "todo_plan": ".resume-site-work/reports/site-todo-plan.md",
  "todo_plan_approval": {
    "status": "user_approved",
    "source": "explicit_user",
    "channel": "conversation"
  },
  "generation_mode": "one-integrated-site",
  "strategy": "single-agent"
}
```

Keep the existing task, dependency, ownership, rollback, and snapshot fields. Change the canonical task from `prototype-shell` to `integrated-site` and the snapshot target to `versions/v1-integrated`.

- [ ] **Step 2: Add failing plan-gate tests**

```python
def test_rejects_missing_readable_todo_plan_path(self) -> None:
    payload = valid_plan()
    payload.pop("todo_plan")
    self.assertEqual(self.run_validator(payload).returncode, 1)

def test_rejects_todo_plan_outside_reports(self) -> None:
    payload = valid_plan()
    payload["todo_plan"] = "docs/site-todo-plan.md"
    self.assertEqual(self.run_validator(payload).returncode, 1)

def test_rejects_unapproved_todo_plan(self) -> None:
    payload = valid_plan()
    payload["todo_plan_approval"]["status"] = "pending"
    self.assertEqual(self.run_validator(payload).returncode, 1)

def test_rejects_browser_todo_plan_approval(self) -> None:
    payload = valid_plan()
    payload["todo_plan_approval"]["channel"] = "browser"
    self.assertEqual(self.run_validator(payload).returncode, 1)

def test_rejects_non_integrated_generation_mode(self) -> None:
    payload = valid_plan()
    payload["generation_mode"] = "prototype-first"
    self.assertEqual(self.run_validator(payload).returncode, 1)

def test_rejects_version_one(self) -> None:
    payload = valid_plan()
    payload["schema_version"] = 1
    result = self.run_validator(payload)
    self.assertEqual(result.returncode, 1)
    self.assertIn("schema_version must be 2", result.stdout)
```

- [ ] **Step 3: Run plan tests and verify RED**

Run:

```powershell
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_validate_site_implementation_plan.py" -v
```

Expected: FAIL because current plans have no readable-plan or explicit-approval fields.

- [ ] **Step 4: Implement plan v2 validation**

Add required fields `todo_plan`, `todo_plan_approval`, and `generation_mode`. Require the normalized path to equal `.resume-site-work/reports/site-todo-plan.md`; require `user_approved`, `explicit_user`, and `conversation`; require `generation_mode == "one-integrated-site"`; preserve all existing multi-agent and file-overlap validation.

- [ ] **Step 5: Update JSON Schema and run tests GREEN**

Run:

```powershell
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_validate_site_implementation_plan.py" -v
```

Expected: all plan-validator tests PASS.

- [ ] **Step 6: Commit the planning gate**

```powershell
git add -- skills/build-resume-portfolio-site/references/site-implementation-plan-schema.json skills/build-resume-portfolio-site/scripts/validate_site_implementation_plan.py skills/build-resume-portfolio-site/scripts/test_validate_site_implementation_plan.py tests/fixtures/site-plan-valid.json
git commit -m "feat: require approved site todo plan"
```

### Task 4: Rewrite discovery and preview contracts around independent categories

**Files:**
- Modify: `skills/build-resume-portfolio-site/references/site-brainstorming-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/visual-style-preview-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/site-planning-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/artifact-layout.md`
- Modify: `tests/test_visual_companion.py`

**Interfaces:**
- Consumes: schema-v3 decisions and the unchanged `launch.cjs`/`stop.cjs` runtime.
- Produces: one independent Gallery draft/session per accepted category and one readable plan artifact.

- [ ] **Step 1: Add failing package-language tests**

Extend `VisualCompanionPackageTests` to require category-neutral placeholders and conversation copy:

```python
self.assertIn("<!-- preview-category -->", text)
self.assertIn("<!-- visual-candidates -->", text)
self.assertIn("return to the conversation", text)
self.assertNotIn("approval", interactive_attributes)
```

Keep the existing form/button/data-choice prohibitions.

- [ ] **Step 2: Run Visual Companion tests and verify RED**

Run:

```powershell
python -m unittest discover -s tests -p "test_visual_companion.py" -v
```

Expected: FAIL because the gallery shell currently exposes only the old visual-directions placeholder.

- [ ] **Step 3: Define the independent Gallery transaction**

In `visual-style-preview-contract.md`, specify category IDs `structure`, `typography`, `color`, `media`, `primary-motion`, and `secondary-motion`; draft paths `.resume-site-work/style-preview/drafts/<category>/<draft-id>/gallery.html`; and separate launch sessions. State verbatim that the Agent must `ask separately for every enabled category`, previews are `independent, not cumulative`, and `declining one category` does not suppress later offers.

- [ ] **Step 4: Define discovery and plan gates**

Rewrite `site-brainstorming-contract.md` with the exact ordered markers from Task 1. Rewrite `site-planning-contract.md` so it creates `site-todo-plan.md`, shows it in conversation, waits for approval, then writes/validates JSON v2. Update artifact layout with category draft/session paths, `site-todo-plan.md`, and `versions/v1-integrated`.

- [ ] **Step 5: Generalize the gallery shell without adding interaction**

Replace `<!-- visual-directions -->` with `<!-- preview-category -->` and `<!-- visual-candidates -->`; use neutral copy that applies to layout, typography, color, media, and motion samples. Do not change server, launcher, token, or stop semantics.

- [ ] **Step 6: Run Visual Companion and behavior tests**

Run:

```powershell
python -m unittest discover -s tests -p "test_visual_companion.py" -v
python -m unittest discover -s tests -p "test_workflow_behavior_contract.py" -v
```

Expected: Visual Companion tests PASS; behavior tests remain RED only for Skill/state-machine integration.

- [ ] **Step 7: Commit the independent-preview contracts**

```powershell
git add -- skills/build-resume-portfolio-site/references/site-brainstorming-contract.md skills/build-resume-portfolio-site/references/visual-style-preview-contract.md skills/build-resume-portfolio-site/references/site-planning-contract.md skills/build-resume-portfolio-site/references/artifact-layout.md skills/build-resume-portfolio-site/assets/visual-companion/gallery-shell.html tests/test_visual_companion.py
git commit -m "docs: define independent design previews"
```

### Task 5: Add the integrated generation resource and validator stage

**Files:**
- Create: `skills/build-resume-portfolio-site/prompts/01-generate-integrated-site.md`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_vite_project.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_validate_vite_project.py`

**Interfaces:**
- Consumes: approved copy, schema-v3 design spec, approved TODO plan, validated JSON plan, authorized media, and design intelligence.
- Produces: complete `.resume-site-work/site` validated with `--stage integrated`.

- [ ] **Step 1: Add failing integrated resource and stage tests**

Require `validate_skill_resources.py --mode runtime --stage integrated` to resolve `generate-integrated-site`, design catalog, media/motion contracts, and capture resources. Add a Vite validator test proving `integrated` requires all normal quality checks plus a `prefers-reduced-motion: reduce` rule.

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```powershell
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_validate_skill_resources.py" -v
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_validate_vite_project.py" -v
```

Expected: FAIL with unknown/missing `integrated` stage and resource.

- [ ] **Step 3: Register the integrated stage**

Add `"generate-integrated-site": "prompts/01-generate-integrated-site.md"` and an `integrated` stage bundle. Add `integrated` to `STAGES` and `MOTION_STAGES` in `validate_vite_project.py` so reduced-motion handling is mandatory for the first complete candidate.

- [ ] **Step 4: Write the integrated generation prompt**

The prompt must require these inputs and outputs explicitly:

```text
Inputs: normalized-resume.json, approved-copy.json, site-design-spec.json,
site-todo-plan.md, site-implementation-plan.json, design-intelligence.json,
authorized media inventory when present.

Output: one complete React + Vite site implementing structure, typography,
color, media treatment, primary motion, compatible secondary motion,
responsive layout, accessibility, coarse-pointer behavior, fallbacks, and
reduced motion in the same source transaction.
```

Remove prototype-language, deferred color/media/motion language, and intermediate confirmation instructions from the new prompt. Retain factual integrity, centralized content data, semantic HTML, approximately 1700px desktop composition, media fallbacks, and build requirements.

- [ ] **Step 5: Run focused tests GREEN**

Run the two focused commands from Step 2. Expected: PASS.

- [ ] **Step 6: Commit integrated generation support**

```powershell
git add -- skills/build-resume-portfolio-site/prompts/01-generate-integrated-site.md skills/build-resume-portfolio-site/scripts/validate_skill_resources.py skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py skills/build-resume-portfolio-site/scripts/validate_vite_project.py skills/build-resume-portfolio-site/scripts/test_validate_vite_project.py
git commit -m "feat: validate integrated portfolio generation"
```

### Task 6: Replace the staged runtime workflow with one integrated transaction

**Files:**
- Modify: `skills/build-resume-portfolio-site/SKILL.md`
- Modify: `skills/build-resume-portfolio-site/references/workflow-contract.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: six confirmed decisions and approved planning artifacts from Tasks 2–4.
- Produces: runtime states `design_<category>_selecting`, `requirements_waiting_confirmation`, `todo_plan_waiting_confirmation`, `integrated_generating`, `integrated_auditing`, `integrated_waiting_confirmation`, `motion_enhancing`, and `complete`.

- [ ] **Step 1: Run the Task 1 behavior suite immediately before edits**

Run:

```powershell
python -m unittest discover -s tests -p "test_workflow_behavior_contract.py" -v
```

Expected: remaining failures identify the old staged Skill and workflow state machine.

- [ ] **Step 2: Rewrite the discovery gate in `SKILL.md`**

Require the six-category transaction, per-category preview question, schema-v3 validation, consolidated requirements approval, readable TODO plan creation, JSON v2 validation, and explicit plan approval. Preserve the rule that no React source edit occurs before both approvals.

- [ ] **Step 3: Replace Stages 1–4 with integrated generation and audit**

Use this runtime sequence:

```text
requirements_waiting_confirmation --confirm-->
todo_plan_generating -> todo_plan_waiting_confirmation --approve-->
integrated_generating -> integrated_auditing ->
integrated_waiting_confirmation
```

Integrated generation consumes `01-generate-integrated-site.md`, validates with `--stage integrated`, builds, promotes, captures desktop/tablet/mobile plus reduced-motion states, performs at most two bounded local repair rounds, and snapshots `versions/v1-integrated`.

- [ ] **Step 4: Implement the three-choice acceptance loop**

Document exact outcomes:

```text
当前效果满意，完成 -> complete
加强动效 -> motion_enhancing -> integrated_waiting_confirmation
提出修改 -> bounded repair OR return to the invalidated core decision
```

Motion enhancement restores `versions/v1-integrated`, changes only the motion layer, revalidates/builds/captures, and preserves content, structure, typography, color, and media. A core-decision reversal invalidates downstream decision evidence, requirements approval, TODO-plan approval, and implementation plan.

- [ ] **Step 5: Preserve optional media search and video upgrade as side transactions**

Retain APIHz and video-upgrade behavior, but rebase their rollback language on the last confirmed integrated or motion-enhanced snapshot rather than `v1-prototype` through `v5-motion-enhanced-poster`.

- [ ] **Step 6: Update README usage narrative**

Describe six optional browser openings, conversational approvals, the TODO plan gate, one-pass React generation, and final accept/enhance/modify choices. State that preview samples are independent and not final-source fragments.

- [ ] **Step 7: Run behavior tests GREEN**

Run:

```powershell
python -m unittest discover -s tests -p "test_workflow_behavior_contract.py" -v
```

Expected: all workflow behavior tests PASS.

- [ ] **Step 8: Commit runtime orchestration**

```powershell
git add -- skills/build-resume-portfolio-site/SKILL.md skills/build-resume-portfolio-site/references/workflow-contract.md README.md
git commit -m "feat: generate portfolio after plan approval"
```

### Task 7: Close cross-resource gaps and regressions

**Files:**
- Modify only when a failing test proves it necessary: `skills/build-resume-portfolio-site/references/creative-direction-contract.md`
- Modify only when a failing test proves it necessary: `skills/build-resume-portfolio-site/references/media-art-direction-contract.md`
- Modify only when a failing test proves it necessary: `skills/build-resume-portfolio-site/references/motion-production-contract.md`
- Modify: `skills/build-resume-portfolio-site/scripts/test_installed_skill_workflow.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_synced_workflow_baseline.py`

**Interfaces:**
- Consumes: completed runtime contracts.
- Produces: no stale staged-confirmation or schema-v2 assumptions in packaged and installed-workflow tests.

- [ ] **Step 1: Search for stale workflow vocabulary**

Run:

```powershell
Get-ChildItem skills/build-resume-portfolio-site,tests -Recurse -File | Select-String -Pattern "schema-version-2|schema_version.*2|prototype_waiting_confirmation|media_direction_waiting_confirmation|motion_waiting_confirmation|v1-prototype|visual_preview"
```

Expected: list every remaining staged assumption; classify each as migration documentation, optional enhancement compatibility, or stale runtime behavior.

- [ ] **Step 2: Add failing installed/sync assertions**

Require the installed Skill workflow tests to find schema v3, `site-todo-plan.md`, `one integrated`, and all three final choices, while rejecting old prototype/media confirmation gates in the main generation path.

- [ ] **Step 3: Run installed-workflow tests and verify RED**

Run:

```powershell
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_installed_skill_workflow.py" -v
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_synced_workflow_baseline.py" -v
```

Expected: FAIL until the source and installed copies are synchronized.

- [ ] **Step 4: Remove only proven stale assumptions**

Update referenced contracts when their old staged input/output descriptions contradict integrated generation. Preserve reusable media inventory, creative-freedom, motion safety, APIHz isolation, and video fallback semantics.

- [ ] **Step 5: Run the entire source test matrix**

Run:

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_*.py" -v
node --check skills/build-resume-portfolio-site/scripts/visual_companion/server.cjs
node --check skills/build-resume-portfolio-site/scripts/visual_companion/launch.cjs
node --check skills/build-resume-portfolio-site/scripts/visual_companion/stop.cjs
```

Expected: all Python tests PASS and all Node syntax checks exit 0.

- [ ] **Step 6: Commit regression cleanup**

Stage only files changed because of failing tests, then commit:

```powershell
git commit -m "test: align packaged portfolio workflow"
```

### Task 8: Validate, synchronize the installed Skill, and update the Draft PR

**Files:**
- Synchronize source files from `skills/build-resume-portfolio-site/` to `C:/Users/86135/.codex/skills/build-resume-portfolio-site/` after approval for the external write.
- No generated workspace artifacts are committed.

**Interfaces:**
- Consumes: verified source Skill at current branch HEAD.
- Produces: matching installed Skill and an updated remote Draft PR.

- [ ] **Step 1: Run source resource validation**

Run:

```powershell
$env:PYTHONUTF8=1
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --stage discovery
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --stage planning
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --stage integrated
python C:/Users/86135/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/build-resume-portfolio-site
```

Expected: every validator exits 0.

- [ ] **Step 2: Synchronize only the Skill package**

After obtaining filesystem approval, copy the verified contents of `skills/build-resume-portfolio-site/` over the installed Skill directory without touching unrelated skills. Exclude `__pycache__`, generated sessions, tests' temporary files, and repository-only docs.

- [ ] **Step 3: Verify source/installed parity**

Hash every packaged file in the source and installed directories using relative paths. Expected: identical file sets and hashes for all packaged resources.

- [ ] **Step 4: Run installed resource and workflow tests**

Run the installed quick validator plus the installed workflow/resource discovery tests. Expected: PASS with schema v3, integrated stage, six preview offers, and TODO-plan approval present.

- [ ] **Step 5: Inspect final Git scope**

Run:

```powershell
git status -sb
git diff --check master...HEAD
git log --oneline master..HEAD
```

Expected: clean worktree, no whitespace errors, and only the approved design/workflow changes.

- [ ] **Step 6: Push and confirm Draft PR**

Push `codex/portable-visual-companion`, then confirm PR #1 remains open as a Draft with base `master` and the new HEAD. Update its body to describe six independent decision previews, schema v3, the approved TODO-plan gate, integrated generation, and the final acceptance loop.

## Final verification checklist

- [ ] Every new validator behavior was observed failing before implementation.
- [ ] Schema v3 accepts declined previews without suppressing later offers.
- [ ] Media skip requires an explicit reason.
- [ ] Primary motion is singular and secondary motion is compatible multi-select.
- [ ] The readable TODO plan and JSON plan approvals are both required.
- [ ] React source remains untouched before final requirements and plan approval.
- [ ] The first generated site integrates every confirmed dimension.
- [ ] Final choices are exactly accept, strengthen motion, or modify.
- [ ] Source and installed Skill packages match.
- [ ] Full Python, Node syntax, resource, and quick-validation suites pass.
