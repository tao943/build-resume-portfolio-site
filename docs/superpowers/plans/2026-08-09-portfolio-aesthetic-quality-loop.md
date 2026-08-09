# Portfolio Aesthetic Quality Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an executable design contract, screenshot-backed dual aesthetic review, anti-template checks, and evidence-linked bounded repair to the portfolio website Skill.

**Architecture:** Compile approved discovery artifacts into a validated `design-contract.json` before React generation. Validate browser evidence through a separate `visual-audit.json` contract that distinguishes identity fit from aesthetic quality, then allow only contract-linked local repairs within the existing two-round loop.

**Tech Stack:** Markdown Skill contracts and prompts, JSON Schema 2020-12 documentation, Python 3 standard-library validators, `unittest`, existing React + Vite and Playwright capture pipeline.

## Global Constraints

- Preserve the six discovery categories and their current ordering and preview-before-selection semantics.
- Generate one integrated website, not multiple complete candidates.
- Content informs identity fit but never proves aesthetic quality.
- Add no npm, Python, native, hosted-model, or external-service dependency.
- Keep build-state schema version `4` and the existing maximum of two completed visual repair rounds.
- Browser activity never selects or approves a design; approval remains conversational.
- Do not modify `competition/` or `services/xinghuo-preview-worker/`.
- Preserve unrelated changes to `.gitignore`, Worker package files, and the lockfile.
- Execute in the current session as a single Agent; do not spawn subagents.
- Synchronize the canonical Skill to the global installed Skill only after all source tests pass.

## File map

- Create `skills/build-resume-portfolio-site/references/design-contract.md`: lifecycle and semantics of the compiled design artifact.
- Create `skills/build-resume-portfolio-site/references/design-contract-schema.json`: public schema documentation for the compiled artifact.
- Create `skills/build-resume-portfolio-site/scripts/validate_design_contract.py`: dependency-free semantic validator.
- Create `skills/build-resume-portfolio-site/scripts/test_validate_design_contract.py`: validator RED/GREEN coverage.
- Create `skills/build-resume-portfolio-site/references/visual-audit-schema.json`: screenshot review report schema.
- Create `skills/build-resume-portfolio-site/scripts/validate_visual_audit.py`: cross-reference validator for captures, rules, statuses, and contract paths.
- Create `skills/build-resume-portfolio-site/scripts/test_validate_visual_audit.py`: audit validator RED/GREEN coverage.
- Modify `tests/test_workflow_behavior_contract.py`: end-to-end ordering and behavior assertions.
- Modify `skills/build-resume-portfolio-site/SKILL.md`: add compilation and dual-audit gates.
- Modify `skills/build-resume-portfolio-site/references/workflow-contract.md`: state transitions and failure behavior.
- Modify `skills/build-resume-portfolio-site/references/artifact-layout.md`: register both new reports and their evidence paths.
- Modify `skills/build-resume-portfolio-site/references/creative-direction-contract.md`: define the compile boundary.
- Modify `skills/build-resume-portfolio-site/references/screenshot-review-rules.md`: deterministic anti-template and dual-dimension review rules.
- Modify `skills/build-resume-portfolio-site/prompts/01-generate-integrated-site.md`: require the validated design contract.
- Modify `skills/build-resume-portfolio-site/prompts/04-audit-screenshot.md`: emit the new visual audit shape.
- Modify `skills/build-resume-portfolio-site/prompts/05-repair-local-issues.md`: replace the unavailable skeleton with bounded production repair instructions.
- Modify `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`: make new artifacts and ready repair prompt stage requirements.
- Modify `skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py`: resource-validator regression coverage.

---

### Task 1: Establish failing workflow behavior tests

**Files:**
- Modify: `tests/test_workflow_behavior_contract.py`

**Interfaces:**
- Consumes: existing `read_skill()` and `read_site_reference()` helpers.
- Produces: behavioral requirements that all later tasks must satisfy.

- [ ] **Step 1: Add focused failing behavior tests**

Append these methods to `WorkflowBehaviorContractTests`:

```python
def test_design_contract_is_compiled_before_react_generation(self) -> None:
    skill = self.read_skill("build-resume-portfolio-site").lower()
    creative = skill.index("creative-direction.json")
    contract = skill.index("design-contract.json")
    source_edit = skill.index("first react source edit")
    self.assertLess(creative, contract)
    self.assertLess(contract, source_edit)
    self.assertIn("validate_design_contract.py", skill)

def test_content_fit_does_not_count_as_aesthetic_approval(self) -> None:
    rules = self.read_site_reference("screenshot-review-rules.md").lower()
    self.assertIn("identity fit", rules)
    self.assertIn("aesthetic quality", rules)
    self.assertIn("cannot compensate", rules)

def test_visual_audit_requires_contract_linked_evidence(self) -> None:
    prompt = (
        ROOT / "skills" / "build-resume-portfolio-site" / "prompts"
        / "04-audit-screenshot.md"
    ).read_text(encoding="utf-8").lower()
    for marker in (
        "evidence_refs",
        "contract_path",
        "identity_fit",
        "aesthetic_quality",
        "validate_visual_audit.py",
    ):
        self.assertIn(marker, prompt)

def test_repair_prompt_is_ready_and_bounded(self) -> None:
    prompt = (
        ROOT / "skills" / "build-resume-portfolio-site" / "prompts"
        / "05-repair-local-issues.md"
    ).read_text(encoding="utf-8").lower()
    self.assertIn("resource_status: ready", prompt)
    self.assertIn("contract_path", prompt)
    self.assertIn("permitted_files", prompt)
    self.assertIn("smallest", prompt)
    self.assertIn("two completed", prompt)
    self.assertNotIn("resource_not_ready", prompt)

def test_anti_template_rules_are_contextual_not_universal_bans(self) -> None:
    rules = self.read_site_reference("screenshot-review-rules.md").lower()
    self.assertIn("anti-template", rules)
    self.assertIn("approved contract", rules)
    self.assertIn("indiscriminate repetition", rules)
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
python tests/test_workflow_behavior_contract.py -v
```

Expected: the five new tests fail because `design-contract.json`, separate
identity/aesthetic review, contract-linked evidence, and a ready repair prompt do
not exist. Existing tests remain green.

- [ ] **Step 3: Commit only the RED tests**

```powershell
git add -- tests/test_workflow_behavior_contract.py
git diff --cached --check
git commit -m "test: define portfolio aesthetic quality loop"
```

---

### Task 2: Add the executable design contract and validator

**Files:**
- Create: `skills/build-resume-portfolio-site/references/design-contract.md`
- Create: `skills/build-resume-portfolio-site/references/design-contract-schema.json`
- Create: `skills/build-resume-portfolio-site/scripts/validate_design_contract.py`
- Create: `skills/build-resume-portfolio-site/scripts/test_validate_design_contract.py`

**Interfaces:**
- Consumes: approved `site-design-spec.json`, `design-intelligence.json`, and `creative-direction.json`.
- Produces: `validate(report: Any) -> list[str]` and validated schema-version-1 `reports/design-contract.json`.

- [ ] **Step 1: Write validator tests first**

Create `test_validate_design_contract.py` with a `valid_report()` helper containing
these exact root keys:

```python
ROOT_FIELDS = {
    "schema_version", "identity_strategy", "signature", "layout",
    "typography", "color", "surface", "motion", "anti_template_rules",
    "acceptance_checks", "traceability",
}
```

Use this common rule shape in `anti_template_rules` and every
`acceptance_checks` group:

```python
{
    "rule_id": "aesthetic.composition.signature-visible",
    "criterion": "The signature structural device remains visible without motion.",
    "evidence_required": ["desktop-initial", "mobile-initial"],
    "severity": "repairable",
}
```

Add these tests after implementing `run_validator()` with the same subprocess
pattern used by `test_validate_creative_direction.py`:

```python
def test_accepts_complete_design_contract(self) -> None:
    result = self.run_validator(valid_report())
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

def test_rejects_missing_signature(self) -> None:
    report = valid_report()
    del report["signature"]
    result = self.run_validator(report)
    self.assertEqual(result.returncode, 1)
    self.assertIn("signature", result.stdout)

def test_rejects_duplicate_rule_ids(self) -> None:
    report = valid_report()
    report["acceptance_checks"]["identity_fit"][0]["rule_id"] = (
        report["anti_template_rules"][0]["rule_id"]
    )
    result = self.run_validator(report)
    self.assertEqual(result.returncode, 1)
    self.assertIn("duplicate rule_id", result.stdout)

def test_rejects_missing_responsive_transformations(self) -> None:
    report = valid_report()
    report["layout"]["responsive_transformations"] = []
    result = self.run_validator(report)
    self.assertEqual(result.returncode, 1)
    self.assertIn("responsive_transformations", result.stdout)

def test_rejects_missing_reduced_motion_or_coarse_pointer_fallback(self) -> None:
    for field in ("reduced_motion", "coarse_pointer", "fallbacks"):
        with self.subTest(field=field):
            report = valid_report()
            report["motion"][field] = []
            result = self.run_validator(report)
            self.assertEqual(result.returncode, 1)
            self.assertIn(field, result.stdout)

def test_rejects_traceability_that_does_not_cover_each_design_section(self) -> None:
    report = valid_report()
    report["traceability"] = [
        item for item in report["traceability"]
        if item["contract_path"] != "signature"
    ]
    result = self.run_validator(report)
    self.assertEqual(result.returncode, 1)
    self.assertIn("traceability must cover signature", result.stdout)

def test_rejects_unknown_traceability_contract_path(self) -> None:
    report = valid_report()
    report["traceability"][0]["contract_path"] = "components.hero"
    result = self.run_validator(report)
    self.assertEqual(result.returncode, 1)
    self.assertIn("unknown contract_path", result.stdout)

def test_cli_does_not_modify_invalid_input(self) -> None:
    report = valid_report()
    del report["signature"]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "design-contract.json"
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        before = path.read_bytes()
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(path.read_bytes(), before)
```

The valid fixture must include exactly one primary motion system, at least one
anti-template rule, non-empty identity and aesthetic acceptance lists, and one
traceability entry for every design section from `identity_strategy` through
`acceptance_checks`.

- [ ] **Step 2: Run validator tests and verify RED**

```powershell
python skills/build-resume-portfolio-site/scripts/test_validate_design_contract.py -v
```

Expected: import or file-not-found failure for `validate_design_contract.py`.

- [ ] **Step 3: Implement the dependency-free validator**

Implement helpers and the public function with this interface:

```python
ALLOWED_SEVERITIES = {"blocking", "repairable", "advisory"}
DESIGN_SECTIONS = {
    "identity_strategy", "signature", "layout", "typography", "color",
    "surface", "motion", "anti_template_rules", "acceptance_checks",
}
ACCEPTANCE_GROUPS = {
    "identity_fit", "aesthetic_quality", "accessibility", "responsive",
    "runtime_safety",
}

def validate(report: Any) -> list[str]:
    """Return stable, human-readable validation errors; return [] when valid."""
```

Validation must enforce exact root fields, schema version 1, required nested
fields, non-empty unique string lists, unique `rule_id` values across both rule
collections, one non-empty primary motion system, responsive transformations,
reduced-motion/coarse-pointer/fallback rules, valid severities, and complete
traceability. Reject React/HTML/source payload keys using the same recursive-walk
pattern as `validate_creative_direction.py`.

CLI behavior:

```python
def main() -> int:
    # positional Path: report
    # print each failure as "ERROR: <message>"
    # success: "OK: design-contract report is valid"
```

The validator reads only; atomic creation remains a workflow requirement using a
temporary sibling followed by replacement after validation.

- [ ] **Step 4: Write the schema and lifecycle contract**

The JSON Schema must mirror the validator, use draft 2020-12,
`additionalProperties: false`, and `$defs` for `nonEmptyStringList` and `rule`.

The Markdown contract must state this exact ordering:

```text
site-design-spec.json + design-intelligence.json + creative-direction.json
-> compile temporary design-contract.json sibling
-> validate_design_contract.py
-> atomically replace reports/design-contract.json
-> first React source edit
```

It must separate identity fit from aesthetic quality, forbid reopening approved
choices, require traceability, and specify that an invalid contract freezes React
edits while preserving the last valid preview.

- [ ] **Step 5: Run focused tests and verify GREEN**

```powershell
python skills/build-resume-portfolio-site/scripts/test_validate_design_contract.py
python skills/build-resume-portfolio-site/scripts/validate_design_contract.py --help
```

Expected: all design-contract tests pass; help exits 0.

- [ ] **Step 6: Commit the design-contract unit**

```powershell
git add -- skills/build-resume-portfolio-site/references/design-contract.md skills/build-resume-portfolio-site/references/design-contract-schema.json skills/build-resume-portfolio-site/scripts/validate_design_contract.py skills/build-resume-portfolio-site/scripts/test_validate_design_contract.py
git diff --cached --check
git commit -m "feat: add executable portfolio design contract"
```

---

### Task 3: Add the screenshot-backed visual audit contract

**Files:**
- Create: `skills/build-resume-portfolio-site/references/visual-audit-schema.json`
- Create: `skills/build-resume-portfolio-site/scripts/validate_visual_audit.py`
- Create: `skills/build-resume-portfolio-site/scripts/test_validate_visual_audit.py`

**Interfaces:**
- Consumes: `visual-audit.json`, `design-contract.json`, and capture IDs created by the existing capture pipeline.
- Produces: `validate(audit: Any, design_contract: Any) -> list[str]` and CLI `validate_visual_audit.py AUDIT --design-contract CONTRACT`.

- [ ] **Step 1: Write failing audit-validator tests**

Use this root shape:

```python
{
    "schema_version": 1,
    "candidate_id": "v1-integrated",
    "design_contract": "reports/design-contract.json",
    "repair_round": 0,
    "captures": [
        {"id": "desktop-initial", "viewport": "desktop", "state": "initial", "path": "captures/desktop.png"},
        {"id": "mobile-initial", "viewport": "mobile", "state": "initial", "path": "captures/mobile.png"},
    ],
    "deterministic_checks": [],
    "dimension_reviews": {
        "identity_fit": {"status": "pass", "verdict": "Specific narrative fit.", "strengths": ["Project priority is visible."], "evidence_refs": ["desktop-initial"], "contract_paths": ["identity_strategy"]},
        "aesthetic_quality": {"status": "repairable", "verdict": "Hierarchy works; rhythm needs repair.", "strengths": ["Signature composition is visible."], "evidence_refs": ["desktop-initial", "mobile-initial"], "contract_paths": ["signature", "layout"]},
    },
    "findings": [],
    "interaction_states_checked": [],
    "overall_status": "repairable",
}
```

Add tests for valid input, unknown evidence reference, unknown rule ID, unknown
contract path, missing identity/aesthetic dimension, blocking finding with a
non-blocking overall status, repair round greater than 2, and a finding without
`permitted_files` or `intended_result`.

- [ ] **Step 2: Run tests and verify RED**

```powershell
python skills/build-resume-portfolio-site/scripts/test_validate_visual_audit.py
```

Expected: file-not-found or import failure for `validate_visual_audit.py`.

- [ ] **Step 3: Implement the validator**

Use these public constants and function:

```python
STATUSES = {"pass", "repairable", "blocking"}
FINDING_DIMENSIONS = {
    "identity_fit", "aesthetic_quality", "accessibility", "responsive",
    "runtime_safety",
}

def validate(audit: Any, design_contract: Any) -> list[str]:
    """Cross-check audit evidence, rules, statuses, and contract paths."""
```

Build the allowed rule set from `anti_template_rules` and every
`acceptance_checks` list. Build allowed contract paths from the design-contract
root sections. Verify capture IDs are unique, every evidence reference exists,
every finding and deterministic check uses a known rule and contract path, and
overall status is at least as severe as its findings and dimension results.

- [ ] **Step 4: Write the matching JSON Schema**

Use draft 2020-12 and strict object shapes. Define `$defs` for `capture`,
`dimensionReview`, `deterministicCheck`, `finding`, and `interactionState`.
Restrict `repair_round` to integers from 0 through 2.

- [ ] **Step 5: Run focused tests and verify GREEN**

```powershell
python skills/build-resume-portfolio-site/scripts/test_validate_visual_audit.py
python skills/build-resume-portfolio-site/scripts/validate_visual_audit.py --help
```

Expected: all visual-audit tests pass; help exits 0.

- [ ] **Step 6: Commit the audit-contract unit**

```powershell
git add -- skills/build-resume-portfolio-site/references/visual-audit-schema.json skills/build-resume-portfolio-site/scripts/validate_visual_audit.py skills/build-resume-portfolio-site/scripts/test_validate_visual_audit.py
git diff --cached --check
git commit -m "feat: validate screenshot-backed aesthetic audits"
```

---

### Task 4: Wire design compilation, dual review, and bounded repair into the Skill

**Files:**
- Modify: `skills/build-resume-portfolio-site/SKILL.md`
- Modify: `skills/build-resume-portfolio-site/references/workflow-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/artifact-layout.md`
- Modify: `skills/build-resume-portfolio-site/references/creative-direction-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/screenshot-review-rules.md`
- Modify: `skills/build-resume-portfolio-site/prompts/01-generate-integrated-site.md`
- Modify: `skills/build-resume-portfolio-site/prompts/04-audit-screenshot.md`
- Modify: `skills/build-resume-portfolio-site/prompts/05-repair-local-issues.md`
- Test: `tests/test_workflow_behavior_contract.py`

**Interfaces:**
- Consumes: validators and schemas from Tasks 2 and 3.
- Produces: an end-to-end workflow that cannot edit React before contract validation and cannot repair without validated audit evidence.

- [ ] **Step 1: Run the Task 1 tests again and confirm they remain RED**

```powershell
python tests/test_workflow_behavior_contract.py -v
```

Expected: only the newly added aesthetic-loop behavior tests fail.

- [ ] **Step 2: Insert design-contract compilation into the canonical workflow**

In `SKILL.md`, add `references/design-contract.md` to startup reading and, after
creative-direction validation, require:

```powershell
python "$SKILL_ROOT\scripts\validate_design_contract.py" `
  ".resume-site-work\reports\design-contract.json"
```

State that the first React source edit occurs only after this command exits 0.
Add `design-contract.json` to the generation prompt's required inputs and require
the implementation to satisfy every applicable signature, design-system,
anti-template, responsive, motion, and acceptance rule.

- [ ] **Step 3: Update workflow and creative-direction boundaries**

Add a `design_contract_compiling` internal state between plan validation and
`integrated_generating`:

```text
implementation_plan_generating --plan validates--> design_contract_compiling
design_contract_compiling --contract validates--> integrated_generating
design_contract_compiling --contract invalid--> artifact_invalid
```

Clarify that creative direction remains expressive and open-ended while the
design contract compiles it into observable implementation commitments without a
new user gate.

Register `reports/design-contract.json` beside `creative-direction.json` and
register `reports/visual-audit.json` as the validated capture-review artifact in
`artifact-layout.md`. State that neither artifact supplies approval semantics.

- [ ] **Step 4: Upgrade screenshot review rules**

Add separate `identity fit` and `aesthetic quality` sections. State explicitly:

```text
A passing identity-fit review cannot compensate for failed aesthetic quality.
A passing aesthetic review cannot compensate for inaccurate or generic identity fit.
```

Add contextual anti-template checks for uniform card repetition, generic centered
hero plus symmetric grid, indiscriminate glass/glow/gradient/pill/radius/shadow
use, missing protagonist/signature device, purposeless motion, and responsive
collapse. A style is not rejected merely because it uses one of these devices;
fail only on conflict with the approved contract, indiscriminate repetition, or
an observable quality/usability defect.

- [ ] **Step 5: Make the audit prompt emit and validate contract-linked evidence**

Update `04-audit-screenshot.md` to require `captures`, `deterministic_checks`,
both `dimension_reviews`, `findings`, and `overall_status`. Every finding must
include:

```json
{
  "id": "finding-001",
  "rule_id": "aesthetic.spacing.rhythm",
  "dimension": "aesthetic_quality",
  "severity": "repairable",
  "viewport_or_state": "desktop-initial",
  "region": "projects",
  "evidence_refs": ["desktop-initial"],
  "contract_path": "layout.section_rhythm",
  "permitted_files": ["src/components/ProjectsSection.jsx", "src/styles/projects.css"],
  "proposed_local_change": "Restore the approved alternating section rhythm.",
  "intended_result": "The primary project regains clear visual priority."
}
```

Require this command before repair:

```powershell
python "$SKILL_ROOT\scripts\validate_visual_audit.py" `
  ".resume-site-work\reports\visual-audit.json" `
  --design-contract ".resume-site-work\reports\design-contract.json"
```

- [ ] **Step 6: Activate the local repair prompt**

Set `resource_version: 1` and `resource_status: ready`. Require the prompt to:

- consume only validated findings with `blocking` or `repairable` severity;
- change only `permitted_files` and the smallest affected DOM/CSS region;
- preserve approved content and all unrelated design-contract paths;
- never select a new style or replace the primary motion system;
- rebuild and recapture all viewports plus affected interaction/fallback states;
- count only completed repairs toward the two-round maximum;
- preserve the last valid preview on validation, build, capture, or audit failure;
- emit `visual_blocked` with evidence after round two when blocking defects remain.

- [ ] **Step 7: Run workflow tests and verify GREEN**

```powershell
python tests/test_workflow_behavior_contract.py -v
```

Expected: all behavior tests pass, including the five Task 1 tests.

- [ ] **Step 8: Commit the integrated workflow**

```powershell
git add -- skills/build-resume-portfolio-site/SKILL.md skills/build-resume-portfolio-site/references/workflow-contract.md skills/build-resume-portfolio-site/references/artifact-layout.md skills/build-resume-portfolio-site/references/creative-direction-contract.md skills/build-resume-portfolio-site/references/screenshot-review-rules.md skills/build-resume-portfolio-site/prompts/01-generate-integrated-site.md skills/build-resume-portfolio-site/prompts/04-audit-screenshot.md skills/build-resume-portfolio-site/prompts/05-repair-local-issues.md
git diff --cached --check
git commit -m "feat: enforce portfolio aesthetic quality loop"
```

---

### Task 5: Enforce resource completeness and verify the canonical Skill

**Files:**
- Modify: `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py`

**Interfaces:**
- Consumes: new references, validators, schemas, and ready prompts.
- Produces: `integrated` resource validation that fails if any aesthetic-loop component is absent or unavailable.

- [ ] **Step 1: Write failing resource-validation tests**

Add `design-contract`, `design-contract-schema`, and `visual-audit-schema` to the
test contract collection. Add these tests:

```python
def test_integrated_stage_requires_aesthetic_quality_resources(self) -> None:
    required = (
        "references/design-contract.md",
        "references/design-contract-schema.json",
        "references/visual-audit-schema.json",
        "scripts/validate_design_contract.py",
        "scripts/validate_visual_audit.py",
    )
    for relative in required:
        with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "skill"
            shutil.copytree(SKILL_ROOT, root)
            (root / relative).unlink()
            report = validate_resources(root, "runtime", "integrated")
            self.assertFalse(report.ok)
            self.assertIn(
                f"missing_aesthetic_quality_file: {relative}",
                report.errors,
            )

def test_integrated_stage_rejects_unready_repair_prompt(self) -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "skill"
        shutil.copytree(SKILL_ROOT, root)
        write_prompt(root, "repair-local-issues", ready=False)
        report = validate_resources(root, "runtime", "integrated")
        self.assertTrue(report.ok, report.errors)
        self.assertFalse(report.ready)
        self.assertIn("resource_not_ready: repair-local-issues", report.errors)
```

- [ ] **Step 2: Run resource tests and verify RED**

```powershell
python skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py
```

Expected: new tests fail because the resource registry does not require these files and `repair-local-issues` is not part of the integrated ready set.

- [ ] **Step 3: Extend the resource registry minimally**

Add contract IDs to `CONTRACT_SPECS`, add validator paths to a new
`AESTHETIC_QUALITY_FILES` tuple, and define `aesthetic-quality-loop` validation
using the existing file-check result type. Set the integrated stage to:

```python
"integrated": (
    "generate-integrated-site",
    "design-catalog",
    "aesthetic-quality-loop",
    "audit-screenshot",
    "repair-local-issues",
),
```

Keep all legacy stage IDs and prompt specifications unchanged.

- [ ] **Step 4: Run focused and full source verification**

```powershell
python skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_*.py" -v
python -m unittest discover -s tests -p "test_*.py" -v
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --skill-root skills/build-resume-portfolio-site --stage integrated
python C:/Users/86135/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/build-resume-portfolio-site
```

Expected: all tests pass, integrated resources report ready, and Skill quick validation succeeds.

- [ ] **Step 5: Commit resource enforcement**

```powershell
git add -- skills/build-resume-portfolio-site/scripts/validate_skill_resources.py skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py
git diff --cached --check
git commit -m "test: require portfolio aesthetic quality resources"
```

---

### Task 6: Synchronize the verified Skill and perform final checks

**Files:**
- Sync source: `skills/build-resume-portfolio-site/`
- Sync destination: `C:/Users/86135/.codex/skills/build-resume-portfolio-site/`
- Preserve: repository-only `docs/`, tests not packaged by the existing sync policy, and all unrelated global Skills.

**Interfaces:**
- Consumes: fully verified canonical Skill at the current commit.
- Produces: discoverable installed Skill with matching packaged file hashes.

- [ ] **Step 1: Verify repository scope before synchronization**

```powershell
git status --short
git diff --check HEAD^
git log -6 --oneline
```

Expected: only the user's pre-existing `.gitignore` and Xinghuo Worker changes remain uncommitted; aesthetic-loop changes are committed.

- [ ] **Step 2: Request filesystem approval and run the existing safe sync mechanism**

Use the repository's established Skill synchronization command or script. If no
script exists, copy only the canonical packaged directories and files after
listing both exact roots. Do not delete unrelated global files and do not use a
recursive destructive command.

- [ ] **Step 3: Compare packaged files and hashes**

Generate relative-path and SHA-256 inventories for the canonical and installed
Skill, excluding repository-only development documentation according to the
existing sync policy. Assert no missing, extra, or mismatched packaged file.

Expected: zero packaged-file differences.

- [ ] **Step 4: Run installed-Skill verification**

```powershell
python C:/Users/86135/.codex/skills/build-resume-portfolio-site/scripts/test_installed_skill_workflow.py
python C:/Users/86135/.codex/skills/.system/skill-creator/scripts/quick_validate.py C:/Users/86135/.codex/skills/build-resume-portfolio-site
```

Expected: installed workflow tests and quick validation pass.

- [ ] **Step 5: Report completion without committing user files**

Report the canonical commit IDs, focused/full test counts, resource-validation
result, quick-validation result, installed hash comparison, and the untouched
user-owned files. Do not push or open a PR unless the user separately requests it.
