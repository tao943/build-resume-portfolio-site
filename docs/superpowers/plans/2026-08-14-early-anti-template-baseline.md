# Early Anti-Template Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate and validate a provisional anti-template baseline before the first visual choice, then require all six category searches and final aggregation to trace back to it.

**Architecture:** Extend the existing database-first discovery protocol with a third report type, `anti_template_baseline`. The same dependency-free Python CLI produces it from the validated content/database baseline, category reports evaluate candidates against its obligations, and approved-discovery aggregation carries it forward so final creative-direction compilation can resolve provisional hypotheses into approved commitments.

**Tech Stack:** Python 3 standard library, JSON Schema documentation, existing vendored UI/UX catalog, `unittest`, Markdown Skill contracts.

## Global Constraints

- Keep runtime dependency-free and offline after installation.
- The provisional artifact is not user approval and cannot authorize React source edits.
- Every anti-template claim must trace to content, reference, or catalog evidence.
- Each category query must inherit the provisional baseline and all previously approved decision IDs.
- Final `creative-direction.json` and `design-contract.json` remain authoritative only after final requirements approval.
- Existing confirmed sites and bounded fast changes remain valid; incomplete legacy discovery must regenerate from baseline.

---

### Task 1: Produce and validate the provisional anti-template baseline

**Files:**
- Create: `skills/build-resume-portfolio-site/scripts/test_early_anti_template_baseline.py`
- Modify: `skills/build-resume-portfolio-site/scripts/portfolio_design_search.py`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_design_discovery.py`
- Modify: `skills/build-resume-portfolio-site/references/design-discovery-schema.json`

**Interfaces:**
- Consumes: `build_baseline(content_map, reference_selection)` output.
- Produces: `build_anti_template_baseline(content_map, baseline) -> dict[str, object]` and CLI command `anti-template-baseline --content-map PATH --baseline PATH --output PATH`.
- Produces report fields: `schema_version`, stable `id`, `report_type`, `mode`, `status`, `query_context`, `evidence_ids`, `visual_protagonist`, `content_form_thesis`, `composition_hypothesis`, `signature_device_candidates`, `template_independence_claim`, `anti_template_rules`, `category_obligations`, and `provenance`.

- [ ] **Step 1: Write failing producer and validator tests**

Create `test_early_anti_template_baseline.py` with a small content map and validated database baseline. Assert:

```python
report = search.build_anti_template_baseline(content_map, baseline)
self.assertEqual(report["report_type"], "anti_template_baseline")
self.assertEqual(report["status"], "provisional_unapproved")
self.assertTrue(report["evidence_ids"])
self.assertEqual(set(report["category_obligations"]), set(search.CATEGORY_DOMAINS))
self.assertEqual(validate.validate(report, "anti_template_baseline"), [])

invalid = copy.deepcopy(report)
invalid["evidence_ids"] = []
self.assertIn(
    "anti-template baseline requires evidence_ids",
    validate.validate(invalid, "anti_template_baseline"),
)
```

Load both scripts with `importlib.util.spec_from_file_location`, matching the repository's standalone-script layout, and patch catalog validation only where a test must avoid reading unrelated files.

- [ ] **Step 2: Run the focused test and verify red state**

Run:

```powershell
python -m unittest skills/build-resume-portfolio-site/scripts/test_early_anti_template_baseline.py -v
```

Expected: FAIL because `build_anti_template_baseline` and the report type do not exist.

- [ ] **Step 3: Implement the minimal baseline builder and CLI command**

In `portfolio_design_search.py`, derive evidence only from baseline candidates, reference IDs, content-map field-path IDs such as `content-map:profile.role`, and catalog source IDs. Use stable IDs and explicit project-context language:

```python
def build_anti_template_baseline(content_map, baseline):
    errors = validate_discovery_report(baseline, expected_type="baseline")
    if errors:
        raise ValueError("baseline design discovery report is invalid")
    selected = next(
        item for item in _sequence(baseline["candidate_directions"])
        if _mapping(item).get("id") == baseline["selected_direction_id"]
    )
    # Build evidence-linked provisional hypotheses and one obligation per
    # CATEGORY_DOMAINS entry; never mark a choice user-approved.
```

Add the CLI parser and branch so the output uses the existing atomic writer.

- [ ] **Step 4: Extend deterministic validation and schema documentation**

Add `_validate_anti_template_baseline()` requiring non-empty evidence, thesis fields, at least one signature candidate and rule, exactly six obligation keys, `status == "provisional_unapproved"`, and valid provenance. Extend `--expected-type` choices and error text to include the new report type. Mirror those requirements in `design-discovery-schema.json` with a third `oneOf` branch.

- [ ] **Step 5: Run focused and syntax checks**

Run:

```powershell
python -m unittest skills/build-resume-portfolio-site/scripts/test_early_anti_template_baseline.py -v
python -m py_compile skills/build-resume-portfolio-site/scripts/portfolio_design_search.py skills/build-resume-portfolio-site/scripts/validate_design_discovery.py
```

Expected: all tests PASS and both scripts compile without output.

- [ ] **Step 6: Commit Task 1**

```powershell
git add -- skills/build-resume-portfolio-site/scripts/test_early_anti_template_baseline.py skills/build-resume-portfolio-site/scripts/portfolio_design_search.py skills/build-resume-portfolio-site/scripts/validate_design_discovery.py skills/build-resume-portfolio-site/references/design-discovery-schema.json
git commit -m "feat: generate early anti-template baseline"
```

### Task 2: Require anti-template inheritance in category search and aggregation

**Files:**
- Modify: `skills/build-resume-portfolio-site/scripts/test_early_anti_template_baseline.py`
- Modify: `skills/build-resume-portfolio-site/scripts/portfolio_design_search.py`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_design_discovery.py`
- Modify: `skills/build-resume-portfolio-site/references/design-discovery-schema.json`
- Modify: `skills/build-resume-portfolio-site/references/design-intelligence-schema.json`
- Modify: `skills/build-resume-portfolio-site/references/design-intelligence-contract.md`

**Interfaces:**
- Changes `search_category(category, content_map, baseline, anti_template_baseline, decisions)`.
- Changes `aggregate_discovery(content_map, baseline, anti_template_baseline, category_reports, design_spec)`.
- Category candidates produce `anti_template_evaluation` with `baseline_rule_ids`, `obligation_ids`, `relationship`, and `rationale`.
- Approved-discovery aggregate produces `anti_template_baseline` and `anti_template_resolution_required: true`.

- [ ] **Step 1: Write failing inheritance tests**

Add tests that patch `_category_candidates` with two deterministic candidates and assert:

```python
report = search.search_category(
    "structure", content_map, baseline, anti_template_baseline, decisions
)
self.assertEqual(
    report["anti_template_baseline_id"], anti_template_baseline["id"]
)
self.assertTrue(report["candidates"][0]["anti_template_evaluation"]["baseline_rule_ids"])
self.assertEqual(validate.validate(report, "category"), [])
```

Add negative cases for a missing baseline ID, an unknown rule ID, absent category obligation, and a candidate whose evaluation relationship is outside `strengthens`, `preserves`, or `conflicts`.

- [ ] **Step 2: Run focused tests and verify red state**

Run the same unittest command. Expected: FAIL because function signatures and evaluation fields are unchanged.

- [ ] **Step 3: Thread the baseline through category search**

Add `--anti-template-baseline` to the category CLI. Validate it before querying. Include its thesis terms in query context, attach the report ID, and generate deterministic evaluations tied to the current category obligation. Keep `conflicts` eligible for presentation but never as the default recommendation; select the first `strengthens` candidate, then `preserves`, and fail if every candidate conflicts.

- [ ] **Step 4: Validate category traceability**

Require the baseline report ID at report level. For every candidate, require non-empty known `baseline_rule_ids`, the current category's obligation ID, allowed relationship enum, and rationale. Update the category schema accordingly.

- [ ] **Step 5: Enforce aggregation continuity**

Add `--anti-template-baseline` to aggregate CLI. Validate it, verify every category report references the same ID, and return:

```python
{
    "anti_template_baseline": dict(anti_template_baseline),
    "anti_template_resolution_required": True,
}
```

Require these fields in approved-discovery mode in `design-intelligence-schema.json` and explain that creative direction must resolve every provisional rule as `adopted`, `refined`, or `rejected_by_approved_choice`, with evidence.

- [ ] **Step 6: Run focused tests and existing resource validation**

Run:

```powershell
python -m unittest skills/build-resume-portfolio-site/scripts/test_early_anti_template_baseline.py -v
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --stage discovery
```

Expected: PASS and `OK` resource validation.

- [ ] **Step 7: Commit Task 2**

```powershell
git add -- skills/build-resume-portfolio-site/scripts/test_early_anti_template_baseline.py skills/build-resume-portfolio-site/scripts/portfolio_design_search.py skills/build-resume-portfolio-site/scripts/validate_design_discovery.py skills/build-resume-portfolio-site/references/design-discovery-schema.json skills/build-resume-portfolio-site/references/design-intelligence-schema.json skills/build-resume-portfolio-site/references/design-intelligence-contract.md
git commit -m "feat: trace visual choices to anti-template baseline"
```

### Task 3: Move the workflow gate before the first visual choice

**Files:**
- Modify: `skills/build-resume-portfolio-site/SKILL.md`
- Modify: `skills/build-resume-portfolio-site/references/workflow-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/site-brainstorming-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/artifact-layout.md`
- Modify: `skills/build-resume-portfolio-site/references/creative-direction-contract.md`
- Modify: `skills/build-resume-portfolio-site/prompts/01-generate-integrated-site.md`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_early_anti_template_baseline.py`

**Interfaces:**
- Adds workflow stages `anti_template_baseline_generating` and `anti_template_baseline_ready` between `design_baseline_ready` and the structure query.
- Adds canonical artifact `reports/design-discovery/anti-template-baseline.json`.
- Final creative direction consumes the aggregate's provisional baseline and resolves it without reopening approved category choices.

- [ ] **Step 1: Write failing workflow-contract assertions**

Add tests that read `SKILL.md` and contracts and require:

```python
self.assertLess(skill.index("anti_template_baseline_generating"), skill.index("--category structure"))
self.assertIn('anti-template-baseline.json" `\n  --expected-type anti_template_baseline', skill)
self.assertIn("--anti-template-baseline", skill)
self.assertIn("provisional_unapproved", creative_direction_contract)
```

Also assert the Skill explicitly says browser preview and user choice remain per-category approvals, while the provisional baseline is not approval.

- [ ] **Step 2: Run focused tests and verify red state**

Run the focused unittest command. Expected: FAIL because the workflow still jumps directly from database baseline to category search.

- [ ] **Step 3: Update Skill commands and ordering**

In `SKILL.md`, insert the generation and validation commands immediately after `design_baseline_ready`:

```powershell
python "$SKILL_ROOT\scripts\portfolio_design_search.py" anti-template-baseline `
  --content-map ".resume-site-work\reports\content-map.json" `
  --baseline ".resume-site-work\reports\design-discovery\baseline.json" `
  --output ".resume-site-work\reports\design-discovery\anti-template-baseline.json"
python "$SKILL_ROOT\scripts\validate_design_discovery.py" `
  ".resume-site-work\reports\design-discovery\anti-template-baseline.json" `
  --expected-type anti_template_baseline
```

Pass `--anti-template-baseline` to all six category commands and aggregate. State that the artifact constrains candidate evaluation but adds no user approval gate.

- [ ] **Step 4: Update contracts and artifact layout**

Document stage transitions, invalidation behavior, artifact paths, category evaluation, legacy in-progress regeneration, and final creative-direction resolution. Do not add a new confirmation step or change final screenshot audit behavior.

- [ ] **Step 5: Register resources and run full verification**

Run:

```powershell
python -m unittest skills/build-resume-portfolio-site/scripts/test_early_anti_template_baseline.py -v
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --stage discovery
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --stage integrated
python -m compileall -q skills/build-resume-portfolio-site/scripts
git diff --check
```

Expected: all tests PASS, both resource stages report `OK`, Python compilation succeeds, and `git diff --check` is silent.

- [ ] **Step 6: Sync and compare the installed Skill**

After source verification, replace only `C:\Users\86135\.codex\skills\build-resume-portfolio-site` from the verified repository Skill directory, then compare recursive file hashes. Do not copy repository docs or Git metadata into the installed Skill.

- [ ] **Step 7: Commit Task 3**

```powershell
git add -- skills/build-resume-portfolio-site/SKILL.md skills/build-resume-portfolio-site/references/workflow-contract.md skills/build-resume-portfolio-site/references/site-brainstorming-contract.md skills/build-resume-portfolio-site/references/artifact-layout.md skills/build-resume-portfolio-site/references/creative-direction-contract.md skills/build-resume-portfolio-site/prompts/01-generate-integrated-site.md skills/build-resume-portfolio-site/scripts/validate_skill_resources.py skills/build-resume-portfolio-site/scripts/test_early_anti_template_baseline.py
git commit -m "feat: require anti-template baseline before visual choices"
```
