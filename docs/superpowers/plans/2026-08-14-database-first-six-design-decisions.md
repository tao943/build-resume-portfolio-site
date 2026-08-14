# Database-First Six Design Decisions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the vendored UI/UX database establish a design baseline before the first visual question and supply evidence-linked candidates for all six visual decisions.

**Architecture:** Extend the existing privacy-safe `portfolio_design_search.py` adapter with baseline, category, and aggregate operations. Persist one validated report per category, require every selected candidate to cite catalog source IDs, and aggregate approved discovery into the canonical design-intelligence report instead of rerunning a late generic recommendation.

**Tech Stack:** Python 3 standard library, vendored BM25 UI/UX catalog, JSON Schema contracts, `unittest`, Markdown Agent Skill workflow.

## Global Constraints

- Keep the Skill self-contained and offline-capable.
- Reuse `vendor/ui-ux-pro-max` and `scripts/portfolio_design_search.py`.
- Add no dependency, cloud service, remote registry, or external runtime Skill.
- Never persist names, contact details, raw resume paragraphs, or project secrets in database queries or design-discovery reports.
- Do not create or edit React source during content, discovery, or planning.
- Browser previews remain independent and display-only; approval remains in the conversation.
- Preserve `recommend` and `enrich` command compatibility.
- Execute in an isolated worktree because the source repository has unrelated uncommitted changes.

---

## File map

- Modify `skills/build-resume-portfolio-site/scripts/portfolio_design_search.py`: baseline, category, retry, and aggregate interfaces.
- Modify `skills/build-resume-portfolio-site/scripts/test_portfolio_design_search.py`: adapter RED/GREEN coverage.
- Create `skills/build-resume-portfolio-site/references/design-discovery-schema.json`: baseline and category report contract.
- Create `skills/build-resume-portfolio-site/scripts/validate_design_discovery.py`: deterministic report validation.
- Create `skills/build-resume-portfolio-site/scripts/test_validate_design_discovery.py`: validator coverage.
- Modify `skills/build-resume-portfolio-site/references/design-intelligence-schema.json`: accept the aggregated approved mode.
- Modify `skills/build-resume-portfolio-site/references/design-intelligence-contract.md`: database-first lifecycle and provenance rules.
- Modify `skills/build-resume-portfolio-site/references/site-design-spec-schema.json`: candidate provenance and discovery-report traceability.
- Modify `skills/build-resume-portfolio-site/scripts/validate_site_design_spec.py`: enforce the same decision provenance.
- Modify `skills/build-resume-portfolio-site/scripts/test_validate_site_design_spec.py`: schema/validator RED/GREEN coverage.
- Modify `skills/build-resume-portfolio-site/SKILL.md`: run baseline before structure and category retrieval before each question.
- Modify `skills/build-resume-portfolio-site/references/site-brainstorming-contract.md`: per-category database transaction.
- Modify `skills/build-resume-portfolio-site/references/workflow-contract.md`: database-ready state transitions and invalidation.
- Modify `skills/build-resume-portfolio-site/references/artifact-layout.md`: discovery report paths and state fields.
- Modify `skills/build-resume-portfolio-site/prompts/01-generate-integrated-site.md`: consume aggregate only.
- Modify `skills/build-resume-portfolio-site/scripts/test_design_intelligence_workflow.py`: workflow-order and no-late-rerun assertions.
- Modify `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`: require discovery schema and validator.
- Modify `skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py`: missing-resource regression.
- Modify `skills/build-resume-portfolio-site/scripts/test_synced_workflow_baseline.py`: installed/source workflow markers.

---

### Task 1: Define the adapter API with failing tests

**Files:**
- Modify: `skills/build-resume-portfolio-site/scripts/test_portfolio_design_search.py`
- Test: `skills/build-resume-portfolio-site/scripts/test_portfolio_design_search.py`

**Interfaces:**
- Consumes: existing `CONTENT_MAP`, current `recommend()` and `_search()` behavior.
- Produces: wished-for `build_baseline()`, `search_category()`, `aggregate_discovery()`, `CATEGORY_DOMAINS`, and `DesignCatalogInsufficient` interfaces.

- [ ] **Step 1: Add failing baseline and domain-map tests**

```python
DECISION_CONTEXT = {
    "structure": {
        "selected_candidate_ids": ["structure-editorial-grid"],
        "approval": {"status": "user_approved"},
    }
}

def test_build_baseline_runs_before_category_search_and_is_privacy_safe(self):
    module = load_search_module()
    result = module.build_baseline(CONTENT_MAP)
    self.assertEqual(result["report_type"], "baseline")
    self.assertEqual(len(result["candidate_directions"]), 3)
    serialized = json.dumps(result, ensure_ascii=False)
    self.assertNotIn("Private Person", serialized)
    self.assertNotIn("person@example.com", serialized)

def test_each_category_has_exact_required_catalog_domains(self):
    module = load_search_module()
    self.assertEqual(module.CATEGORY_DOMAINS, {
        "structure": ("landing", "style", "product", "ux"),
        "typography": ("typography", "style", "ux"),
        "color": ("color", "style", "ux"),
        "media": ("style", "product", "landing", "ux"),
        "primary_motion": ("motion", "style", "landing", "ux"),
        "secondary_motion": ("motion", "react", "ux"),
    })
```

- [ ] **Step 2: Add failing inheritance, provenance, and insufficiency tests**

```python
def test_typography_search_inherits_approved_structure(self):
    module = load_search_module()
    baseline = module.build_baseline(CONTENT_MAP)
    report = module.search_category(
        "typography", CONTENT_MAP, baseline, DECISION_CONTEXT
    )
    self.assertEqual(report["inherited_decision_ids"], ["structure-editorial-grid"])
    self.assertEqual(report["domains_searched"], ["typography", "style", "ux"])
    self.assertTrue(all(item["source_ids"] for item in report["candidates"]))

def test_category_search_never_fabricates_when_catalog_is_insufficient(self):
    module = load_search_module()
    baseline = module.build_baseline(CONTENT_MAP)
    original = module._search
    module._search = lambda domain, query, count=8: []
    try:
        with self.assertRaisesRegex(
            module.DesignCatalogInsufficient, "design_catalog_insufficient"
        ):
            module.search_category("color", CONTENT_MAP, baseline, {})
    finally:
        module._search = original
```

- [ ] **Step 3: Run the adapter tests and verify RED**

Run:

```powershell
python skills\build-resume-portfolio-site\scripts\test_portfolio_design_search.py
```

Expected: FAIL because `build_baseline`, `search_category`,
`aggregate_discovery`, `CATEGORY_DOMAINS`, and `DesignCatalogInsufficient` do
not exist.

- [ ] **Step 4: Commit the RED tests**

```powershell
git add skills/build-resume-portfolio-site/scripts/test_portfolio_design_search.py
git commit -m "test: define database-first discovery adapter"
```

---

### Task 2: Implement baseline and per-category catalog retrieval

**Files:**
- Modify: `skills/build-resume-portfolio-site/scripts/portfolio_design_search.py`
- Test: `skills/build-resume-portfolio-site/scripts/test_portfolio_design_search.py`

**Interfaces:**
- Consumes: privacy-safe content profile, baseline report, approved decision map.
- Produces:
  - `build_baseline(content_map, reference_selection=None) -> dict[str, object]`
  - `search_category(category, content_map, baseline, decisions) -> dict[str, object]`
  - CLI commands `baseline` and `category`.

- [ ] **Step 1: Add category constants and the typed insufficiency error**

```python
CATEGORY_DOMAINS = {
    "structure": ("landing", "style", "product", "ux"),
    "typography": ("typography", "style", "ux"),
    "color": ("color", "style", "ux"),
    "media": ("style", "product", "landing", "ux"),
    "primary_motion": ("motion", "style", "landing", "ux"),
    "secondary_motion": ("motion", "react", "ux"),
}

class DesignCatalogInsufficient(RuntimeError):
    pass
```

- [ ] **Step 2: Implement privacy-safe inherited query context**

```python
def _approved_decision_ids(decisions: Mapping[str, object]) -> list[str]:
    result: list[str] = []
    for category in CATEGORY_DOMAINS:
        decision = _mapping(decisions.get(category))
        approval = _mapping(decision.get("approval"))
        if approval.get("status") != "user_approved":
            continue
        result.extend(
            _string(item)
            for item in _sequence(decision.get("selected_candidate_ids"))
            if _string(item)
        )
    return result

def _category_query_context(
    content_map: Mapping[str, object],
    baseline: Mapping[str, object],
    decisions: Mapping[str, object],
) -> dict[str, object]:
    profile = _content_profile(content_map)
    selected_direction = _string(baseline.get("selected_direction_id"))
    return {
        **profile,
        "baseline_direction_id": selected_direction,
        "approved_decision_ids": _approved_decision_ids(decisions),
    }
```

- [ ] **Step 3: Implement the baseline wrapper**

```python
def build_baseline(
    content_map: Mapping[str, object],
    reference_selection: Mapping[str, object] | None = None,
) -> dict[str, object]:
    report = recommend(content_map)
    report["mode"] = "baseline"
    report["report_type"] = "baseline"
    report["reference_selection_ids"] = _unique_tokens(
        _safe_tokens(reference_selection or {}), limit=8
    )
    return report
```

- [ ] **Step 4: Implement category candidate projection and one bounded retry**

Use domain-specific row adapters so every candidate has one stable shape:

```python
DOMAIN_ID_KEYS = {
    "landing": "Pattern Name",
    "style": "Style Category",
    "product": "Product Type",
    "typography": "Font Pairing Name",
    "color": "Product Type",
    "motion": "Category",
    "react": "Guideline",
    "ux": "Issue",
}

def _row_label(domain: str, row: Mapping[str, object]) -> str:
    return _string(row.get(DOMAIN_ID_KEYS[domain]), domain)

def _row_notes(row: Mapping[str, object]) -> list[str]:
    keys = (
        "Best For", "Description", "Do", "Notes", "Key Considerations",
        "Effects & Animation", "Mood/Style Keywords", "Guideline",
    )
    return [_string(row.get(key)) for key in keys if _string(row.get(key))]

def _category_candidate(
    category: str,
    index: int,
    rows: Mapping[str, Mapping[str, object]],
    inherited_ids: Sequence[str],
) -> dict[str, object]:
    source_ids = [
        _source_id(domain, row, DOMAIN_ID_KEYS[domain])
        for domain, row in rows.items()
        if row
    ]
    labels = [_row_label(domain, row) for domain, row in rows.items() if row]
    notes = [note for row in rows.values() for note in _row_notes(row)]
    return {
        "id": f"{category}-{index + 1}",
        "label": " · ".join(labels[:2]),
        "fit": notes[:2] or [f"Catalog fit for {category}"],
        "risks": notes[2:4] or ["Verify content fit and implementation cost"],
        "tradeoffs": notes[4:6] or ["Balance expression, readability, and cost"],
        "compatibility": list(inherited_ids),
        "responsive_fallback": "Preserve semantic order in a single-column document flow",
        "accessibility_notes": [
            note for note in notes if any(
                term in note.casefold()
                for term in ("access", "contrast", "focus", "motion", "touch")
            )
        ][:3] or ["Verify focus, contrast, touch, and reduced-motion behavior"],
        "source_ids": source_ids,
    }
```

Add the complete search loop:

```python
def _category_candidates(
    category: str,
    query: str,
    inherited_ids: Sequence[str],
) -> list[dict[str, object]]:
    domains = CATEGORY_DOMAINS[category]
    rows_by_domain = {domain: _search(domain, query, 8) for domain in domains}
    available = min((len(rows) for rows in rows_by_domain.values()), default=0)
    return [
        _category_candidate(
            category,
            index,
            {domain: rows[index] for domain, rows in rows_by_domain.items()},
            inherited_ids,
        )
        for index in range(min(available, 3))
    ]

def search_category(
    category: str,
    content_map: Mapping[str, object],
    baseline: Mapping[str, object],
    decisions: Mapping[str, object],
) -> dict[str, object]:
    if category not in CATEGORY_DOMAINS:
        raise ValueError(f"unsupported design category: {category}")
    context = _category_query_context(content_map, baseline, decisions)
    inherited_ids = list(context["approved_decision_ids"])
    full_query = _query_text(
        context,
        " ".join([category, _string(context["baseline_direction_id"]), *inherited_ids]),
    )
    candidates = _category_candidates(category, full_query, inherited_ids)
    if len(candidates) < 2:
        broad_query = " ".join(
            filter(None, (
                _string(context["role"]), _string(context["industry"]),
                _string(context["content_density"]), _string(context["media_profile"]),
                _string(context["baseline_direction_id"]), *inherited_ids, category,
            ))
        )
        candidates = _category_candidates(category, broad_query, inherited_ids)
    if len(candidates) < 2:
        raise DesignCatalogInsufficient(
            "design_catalog_insufficient: "
            f"category={category}; domains={','.join(CATEGORY_DOMAINS[category])}; "
            f"found={len(candidates)}; required=2"
        )
    return {
        "schema_version": 1,
        "report_type": "category",
        "category": category,
        "query_context": context,
        "domains_searched": list(CATEGORY_DOMAINS[category]),
        "inherited_decision_ids": inherited_ids,
        "candidates": candidates,
        "recommended_candidate_id": candidates[0]["id"],
        "provenance": {
            "upstream": UPSTREAM,
            "catalog_version": validate_catalog(CATALOG_ROOT).catalog_version,
        },
    }
```

If both attempts still produce fewer than two candidates, the function raises
the exact `DesignCatalogInsufficient` error shown above.

```python
raise DesignCatalogInsufficient(
    "design_catalog_insufficient: "
    f"category={category}; domains={','.join(domains)}; "
    f"found={len(candidates)}; required=2"
)
```

- [ ] **Step 5: Add `baseline` and `category` CLI parsers**

```python
baseline_parser = subparsers.add_parser("baseline")
baseline_parser.add_argument("--content-map", type=Path, required=True)
baseline_parser.add_argument("--reference-selection", type=Path)
baseline_parser.add_argument("--output", type=Path, required=True)

category_parser = subparsers.add_parser("category")
category_parser.add_argument("--category", choices=tuple(CATEGORY_DOMAINS), required=True)
category_parser.add_argument("--content-map", type=Path, required=True)
category_parser.add_argument("--baseline", type=Path, required=True)
category_parser.add_argument("--decisions", type=Path, required=True)
category_parser.add_argument("--output", type=Path, required=True)
```

Return exit `3` for `DesignCatalogInsufficient`, exit `2` for invalid input, and
exit `1` for catalog or filesystem failure.

- [ ] **Step 6: Run adapter tests and verify GREEN**

Run:

```powershell
python skills\build-resume-portfolio-site\scripts\test_portfolio_design_search.py
```

Expected: all adapter tests PASS, including existing `recommend` and `enrich`.

- [ ] **Step 7: Commit the adapter implementation**

```powershell
git add skills/build-resume-portfolio-site/scripts/portfolio_design_search.py
git commit -m "feat: query design catalog throughout discovery"
```

---

### Task 3: Add deterministic discovery-report validation

**Files:**
- Create: `skills/build-resume-portfolio-site/references/design-discovery-schema.json`
- Create: `skills/build-resume-portfolio-site/scripts/validate_design_discovery.py`
- Create: `skills/build-resume-portfolio-site/scripts/test_validate_design_discovery.py`

**Interfaces:**
- Consumes: baseline or category JSON report.
- Produces: `validate(payload: object, expected_type: str | None = None) -> list[str]` and CLI exit `0/1`.

- [ ] **Step 1: Write validator tests before schema or validator**

Cover:

```python
from copy import deepcopy

VALID_CANDIDATE = {
    "id": "typography-1",
    "label": "Editorial Serif · Quiet Sans",
    "fit": ["Readable technical editorial hierarchy"],
    "risks": ["Verify Chinese fallback metrics"],
    "tradeoffs": ["Distinctive headings with restrained body text"],
    "compatibility": ["structure-editorial-grid"],
    "responsive_fallback": "Single-column document flow",
    "accessibility_notes": ["Preserve contrast and readable line length"],
    "source_ids": ["typography:editorial-serif", "style:editorial"],
}
VALID_CATEGORY = {
    "schema_version": 1,
    "report_type": "category",
    "category": "typography",
    "query_context": {
        "role": "AI application developer",
        "industry": "technology",
        "content_density": "high",
        "media_profile": "limited",
        "keywords": ["React", "Python"],
        "baseline_direction_id": "direction-1",
        "approved_decision_ids": ["structure-editorial-grid"],
    },
    "domains_searched": ["typography", "style", "ux"],
    "inherited_decision_ids": ["structure-editorial-grid"],
    "candidates": [
        VALID_CANDIDATE,
        {**VALID_CANDIDATE, "id": "typography-2", "label": "Technical Sans"},
    ],
    "recommended_candidate_id": "typography-1",
    "provenance": {"upstream": "nextlevelbuilder/ui-ux-pro-max-skill", "catalog_version": "2.11.0"},
}

def test_valid_category_report_passes(self):
    self.assertEqual(validate(deepcopy(VALID_CATEGORY)), [])

def test_candidate_without_source_ids_fails(self):
    payload = deepcopy(VALID_CATEGORY)
    payload["candidates"][0]["source_ids"] = []
    self.assertIn("candidate typography-1 requires source_ids", validate(payload))

def test_category_with_wrong_domains_fails(self):
    payload = deepcopy(VALID_CATEGORY)
    payload["domains_searched"] = ["color"]
    self.assertIn("typography domains do not match contract", validate(payload))

def test_duplicate_candidate_ids_fail(self):
    payload = deepcopy(VALID_CATEGORY)
    payload["candidates"][1]["id"] = "typography-1"
    self.assertIn("candidate IDs must be unique", validate(payload))

def test_inherited_decisions_must_match_query_context(self):
    payload = deepcopy(VALID_CATEGORY)
    payload["query_context"]["approved_decision_ids"] = []
    self.assertIn("inherited decisions do not match query context", validate(payload))

def test_baseline_requires_exactly_three_directions(self):
    payload = {
        "schema_version": 1,
        "report_type": "baseline",
        "mode": "baseline",
        "query": VALID_CATEGORY["query_context"] | {
            "baseline_direction_id": "",
            "approved_decision_ids": [],
        },
        "candidate_directions": [VALID_CANDIDATE, VALID_CANDIDATE],
        "selected_direction_id": "typography-1",
        "guardrails": [],
        "react_guidelines": [],
        "reference_selection_ids": [],
        "provenance": VALID_CATEGORY["provenance"] | {"domains": ["style"]},
    }
    self.assertIn("baseline requires exactly three directions", validate(payload))
```

- [ ] **Step 2: Run the validator test and verify RED**

Run:

```powershell
python skills\build-resume-portfolio-site\scripts\test_validate_design_discovery.py
```

Expected: FAIL because `validate_design_discovery.py` does not exist.

- [ ] **Step 3: Write `design-discovery-schema.json`**

Use a `oneOf` baseline/category schema. A category candidate must require:

```json
[
  "id",
  "label",
  "fit",
  "risks",
  "tradeoffs",
  "compatibility",
  "responsive_fallback",
  "accessibility_notes",
  "source_ids"
]
```

Require `schema_version: 1`, catalog version, exact domains, privacy-safe query
context, recommendation ID, and at least two candidates. Baseline requires
exactly three complete directions.

- [ ] **Step 4: Implement semantic validation**

```python
EXPECTED_DOMAINS = {
    "structure": ["landing", "style", "product", "ux"],
    "typography": ["typography", "style", "ux"],
    "color": ["color", "style", "ux"],
    "media": ["style", "product", "landing", "ux"],
    "primary_motion": ["motion", "style", "landing", "ux"],
    "secondary_motion": ["motion", "react", "ux"],
}

def _strings(value: object, *, non_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not non_empty)
        and all(isinstance(item, str) and item.strip() for item in value)
    )

def validate(payload: object, expected_type: str | None = None) -> list[str]:
    if not isinstance(payload, dict):
        return ["design discovery report must be an object"]
    errors: list[str] = []
    report_type = payload.get("report_type")
    if expected_type is not None and report_type != expected_type:
        errors.append(f"expected report type: {expected_type}")
    if report_type == "baseline":
        directions = payload.get("candidate_directions")
        if not isinstance(directions, list) or len(directions) != 3:
            errors.append("baseline requires exactly three directions")
        return errors
    if report_type != "category":
        return errors + ["report_type must be baseline or category"]
    category = payload.get("category")
    if category not in EXPECTED_DOMAINS:
        return errors + ["unsupported design category"]
    if payload.get("domains_searched") != EXPECTED_DOMAINS[category]:
        errors.append(f"{category} domains do not match contract")
    inherited = payload.get("inherited_decision_ids")
    context = payload.get("query_context")
    if not isinstance(context, dict) or inherited != context.get("approved_decision_ids"):
        errors.append("inherited decisions do not match query context")
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or len(candidates) < 2:
        errors.append("category requires at least two candidates")
        candidates = []
    ids: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("candidate must be an object")
            continue
        candidate_id = str(candidate.get("id", ""))
        ids.append(candidate_id)
        if not _strings(candidate.get("source_ids"), non_empty=True):
            errors.append(f"candidate {candidate_id} requires source_ids")
    if len(ids) != len(set(ids)):
        errors.append("candidate IDs must be unique")
    if payload.get("recommended_candidate_id") not in ids:
        errors.append("recommendation must reference a candidate")
    return errors
```

The CLI prints `OK: design discovery report is valid` on success.

- [ ] **Step 5: Run validator tests and verify GREEN**

```powershell
python skills\build-resume-portfolio-site\scripts\test_validate_design_discovery.py
```

Expected: all validator tests PASS.

- [ ] **Step 6: Commit schema and validator**

```powershell
git add skills/build-resume-portfolio-site/references/design-discovery-schema.json skills/build-resume-portfolio-site/scripts/validate_design_discovery.py skills/build-resume-portfolio-site/scripts/test_validate_design_discovery.py
git commit -m "feat: validate design discovery evidence"
```

---

### Task 4: Bind database evidence into approved site decisions

**Files:**
- Modify: `skills/build-resume-portfolio-site/references/site-design-spec-schema.json`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_site_design_spec.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_validate_site_design_spec.py`

**Interfaces:**
- Consumes: category candidate records and report paths.
- Produces: confirmed decisions whose candidates contain provenance and whose selected IDs exist in the cited discovery report.

- [ ] **Step 1: Add failing provenance tests**

```python
def test_confirmed_candidate_requires_source_ids(self):
    payload = valid_payload()
    del payload["decisions"]["structure"]["candidates"][0]["source_ids"]
    self.assertIn("structure candidate[0] requires source_ids", validate(payload))

def test_confirmed_decision_requires_discovery_report(self):
    payload = valid_payload()
    del payload["decisions"]["typography"]["discovery_report"]
    self.assertIn("typography requires a discovery report", validate(payload))
```

- [ ] **Step 2: Run the site-design validator tests and verify RED**

```powershell
python skills\build-resume-portfolio-site\scripts\test_validate_site_design_spec.py
```

Expected: new assertions FAIL because candidate provenance and discovery paths
are not required.

- [ ] **Step 3: Extend decision candidates and decision records**

Add required candidate fields `fit`, `risks`, `compatibility`,
`responsive_fallback`, `accessibility_notes`, and `source_ids`. Add required
decision field:

```json
"discovery_report": {
  "type": "string",
  "pattern": "^\\.resume-site-work/reports/design-discovery/(structure|typography|color|media|primary-motion|secondary-motion)\\.json$"
}
```

For skipped media, require `approval` in addition to `skip_reason`.

- [ ] **Step 4: Implement equivalent semantic checks**

Update `_validate_candidates()` and `_validate_confirmed_decision()` to require
nonempty source IDs and the exact category report path. Preserve conversation-
only approval and existing candidate-membership checks.

- [ ] **Step 5: Run validator tests and verify GREEN**

```powershell
python skills\build-resume-portfolio-site\scripts\test_validate_site_design_spec.py
```

Expected: all tests PASS.

- [ ] **Step 6: Commit approved-decision provenance**

```powershell
git add skills/build-resume-portfolio-site/references/site-design-spec-schema.json skills/build-resume-portfolio-site/scripts/validate_site_design_spec.py skills/build-resume-portfolio-site/scripts/test_validate_site_design_spec.py
git commit -m "feat: trace site decisions to catalog evidence"
```

---

### Task 5: Move catalog retrieval into the discovery workflow

**Files:**
- Modify: `skills/build-resume-portfolio-site/SKILL.md`
- Modify: `skills/build-resume-portfolio-site/references/site-brainstorming-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/workflow-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/artifact-layout.md`
- Modify: `skills/build-resume-portfolio-site/scripts/test_design_intelligence_workflow.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_synced_workflow_baseline.py`

**Interfaces:**
- Consumes: `CONTENT_READY`, content map, reference selection, baseline and category reports.
- Produces: database-ready state before questions and invalidation rules after changed decisions.

- [ ] **Step 1: Add failing workflow-order tests**

```python
def test_database_baseline_precedes_first_structure_question(self):
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    baseline = skill.index("portfolio_design_search.py\" baseline")
    structure = skill.index("overall structure")
    self.assertLess(baseline, structure)

def test_every_visual_category_has_a_database_query(self):
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    for category in (
        "structure", "typography", "color", "media",
        "primary_motion", "secondary_motion",
    ):
        self.assertIn(f"--category {category}", skill)

def test_discovery_resources_require_design_catalog(self):
    self.assertIn("design-catalog", STAGE_RESOURCES["discovery"])
```

- [ ] **Step 2: Run workflow tests and verify RED**

```powershell
python skills\build-resume-portfolio-site\scripts\test_design_intelligence_workflow.py
python skills\build-resume-portfolio-site\scripts\test_synced_workflow_baseline.py
```

Expected: FAIL because design search is still documented near React generation
and discovery does not require the catalog.

- [ ] **Step 3: Update the Skill discovery sequence**

Immediately after `CONTENT_READY`:

```powershell
python "$SKILL_ROOT\scripts\portfolio_design_search.py" baseline `
  --content-map ".resume-site-work\reports\content-map.json" `
  --output ".resume-site-work\reports\design-discovery\baseline.json"
```

Before each category's candidates, require:

```powershell
python "$SKILL_ROOT\scripts\portfolio_design_search.py" category `
  --category <category-id> `
  --content-map ".resume-site-work\reports\content-map.json" `
  --baseline ".resume-site-work\reports\design-discovery\baseline.json" `
  --decisions ".resume-site-work\reports\design-decisions-working.json" `
  --output ".resume-site-work\reports\design-discovery\<category-file>.json"
```

Validate each report before presenting candidates. Preserve the existing order,
separate browser offer, independent Gallery, conversational approval, and lock.

- [ ] **Step 4: Update state and invalidation contracts**

Add states:

```text
design_baseline_generating
design_baseline_ready
design_<category>_querying
design_<category>_selecting
```

Record `design_discovery.baseline` and six category paths in build state. A
changed category invalidates only downstream reports, final requirements
approval, TODO approval, and implementation plan.

- [ ] **Step 5: Run workflow tests and verify GREEN**

Run the two focused workflow test files again. Expected: PASS.

- [ ] **Step 6: Commit database-first workflow documentation**

```powershell
git add skills/build-resume-portfolio-site/SKILL.md skills/build-resume-portfolio-site/references/site-brainstorming-contract.md skills/build-resume-portfolio-site/references/workflow-contract.md skills/build-resume-portfolio-site/references/artifact-layout.md skills/build-resume-portfolio-site/scripts/test_design_intelligence_workflow.py skills/build-resume-portfolio-site/scripts/test_synced_workflow_baseline.py
git commit -m "feat: run design database before every visual choice"
```

---

### Task 6: Aggregate approved discovery for integrated generation

**Files:**
- Modify: `skills/build-resume-portfolio-site/scripts/portfolio_design_search.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_portfolio_design_search.py`
- Modify: `skills/build-resume-portfolio-site/references/design-intelligence-schema.json`
- Modify: `skills/build-resume-portfolio-site/references/design-intelligence-contract.md`
- Modify: `skills/build-resume-portfolio-site/prompts/01-generate-integrated-site.md`
- Modify: `skills/build-resume-portfolio-site/SKILL.md`
- Modify: `skills/build-resume-portfolio-site/scripts/test_design_intelligence_workflow.py`

**Interfaces:**
- Consumes: baseline, six valid category reports, approved site design spec.
- Produces: canonical `design-intelligence.json` with `mode: "approved-discovery"`.

- [ ] **Step 1: Add failing aggregation tests**

```python
def test_aggregate_preserves_all_approved_category_ids(self):
    module = load_search_module()
    baseline = module.build_baseline(CONTENT_MAP)
    decisions = {}
    reports = {}
    for category in module.CATEGORY_DOMAINS:
        report = module.search_category(
            category, CONTENT_MAP, baseline, decisions
        )
        reports[category] = report
        selected = report["recommended_candidate_id"]
        decisions[category] = {
            "selected_candidate_ids": [selected],
            "discovery_report": (
                ".resume-site-work/reports/design-discovery/"
                + category.replace("_", "-")
                + ".json"
            ),
            "approval": {"status": "user_approved"},
        }
    result = module.aggregate_discovery(
        CONTENT_MAP, baseline, reports, {"decisions": decisions}
    )
    self.assertEqual(result["mode"], "approved-discovery")
    self.assertEqual(set(result["approved_decisions"]), {
        "structure", "typography", "color", "media",
        "primary_motion", "secondary_motion",
    })

def test_generation_workflow_does_not_rerun_generic_recommend(self):
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    generation = skill.split("## Generate one integrated website", 1)[1]
    self.assertNotIn(" portfolio_design_search.py\" recommend", generation)
    self.assertIn(" portfolio_design_search.py\" aggregate", generation)
```

- [ ] **Step 2: Run focused tests and verify RED**

Expected: FAIL because aggregate mode is missing and generation reruns recommend.

- [ ] **Step 3: Implement aggregate behavior and CLI**

```python
def aggregate_discovery(
    content_map: Mapping[str, object],
    baseline: Mapping[str, object],
    category_reports: Mapping[str, object],
    design_spec: Mapping[str, object],
) -> dict[str, object]:
    decisions = _mapping(design_spec.get("decisions"))
    return {
        "schema_version": 1,
        "mode": "approved-discovery",
        "query": _content_profile(content_map),
        "baseline": baseline,
        "approved_decisions": {
            category: {
                "selected_candidate_ids": _mapping(decisions.get(category)).get(
                    "selected_candidate_ids", []
                ),
                "discovery_report": _mapping(decisions.get(category)).get(
                    "discovery_report"
                ),
            }
            for category in CATEGORY_DOMAINS
        },
        "guardrails": baseline.get("guardrails", []),
        "react_guidelines": baseline.get("react_guidelines", []),
        "provenance": baseline["provenance"],
    }
```

Add CLI `aggregate --content-map --baseline --reports-dir --site-design-spec
--output`. Validate every input report before atomic output replacement.

- [ ] **Step 4: Extend the canonical schema and generation prompt**

Add `approved-discovery` to `mode`, with required `baseline` and
`approved_decisions`. Update the prompt to treat selected category candidates
as fixed input and database open fields as implementation freedom.

- [ ] **Step 5: Run adapter and workflow tests and verify GREEN**

```powershell
python skills\build-resume-portfolio-site\scripts\test_portfolio_design_search.py
python skills\build-resume-portfolio-site\scripts\test_design_intelligence_workflow.py
```

Expected: PASS.

- [ ] **Step 6: Commit aggregation**

```powershell
git add skills/build-resume-portfolio-site/scripts/portfolio_design_search.py skills/build-resume-portfolio-site/scripts/test_portfolio_design_search.py skills/build-resume-portfolio-site/references/design-intelligence-schema.json skills/build-resume-portfolio-site/references/design-intelligence-contract.md skills/build-resume-portfolio-site/prompts/01-generate-integrated-site.md skills/build-resume-portfolio-site/SKILL.md skills/build-resume-portfolio-site/scripts/test_design_intelligence_workflow.py
git commit -m "feat: compile approved design discovery"
```

---

### Task 7: Register resources, verify, and synchronize the active Skill

**Files:**
- Modify: `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py`
- Verify: `skills/build-resume-portfolio-site/`
- Synchronize after verification: `C:/Users/86135/.codex/skills/build-resume-portfolio-site/`

**Interfaces:**
- Consumes: verified source Skill.
- Produces: resource-complete source and matching active local installation.

- [ ] **Step 1: Add failing missing-resource tests**

Require discovery stage and skeleton mode to include:

```python
DESIGN_DISCOVERY_FILES = (
    "references/design-discovery-schema.json",
    "scripts/validate_design_discovery.py",
    "scripts/portfolio_design_search.py",
)
```

Delete each file in a temporary copied Skill and assert
`missing_design_discovery_file: <path>`.

- [ ] **Step 2: Run resource tests and verify RED**

```powershell
python skills\build-resume-portfolio-site\scripts\test_validate_skill_resources.py
```

Expected: FAIL because the files are not registered.

- [ ] **Step 3: Register and validate discovery resources**

Add `design-discovery` to the skeleton and `discovery` stage. Validate every
JSON file as an object and every Python/Markdown file as nonempty.

- [ ] **Step 4: Run focused and complete verification**

```powershell
python -m unittest discover -s tests
python -m unittest discover -s skills\build-resume-portfolio-site\scripts -p "test_*.py"
python -X utf8 C:\Users\86135\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills\build-resume-portfolio-site
python skills\build-resume-portfolio-site\scripts\validate_skill_resources.py --mode skeleton --skill-root skills\build-resume-portfolio-site
git diff --check
Get-ChildItem -Recurse -File skills\build-resume-portfolio-site\scripts -Filter *.cjs | ForEach-Object { node --check $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
```

Expected: all repository and Skill tests PASS; structural/resource validation
returns success; diff and Node checks produce no errors.

- [ ] **Step 5: Scan production resources**

Exclude `test_*.py` and scan for removed external-sub-Skill routes, remote
registries, recipe systems, platform branding, and privacy-sensitive fixture
values. Expected: no production hits.

- [ ] **Step 6: Commit resource registration**

```powershell
git add skills/build-resume-portfolio-site/scripts/validate_skill_resources.py skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py
git commit -m "test: require database-first discovery resources"
```

- [ ] **Step 7: Synchronize the verified Skill**

Compare source and active-install manifests first. Copy the verified source Skill
to `C:/Users/86135/.codex/skills/build-resume-portfolio-site/` while excluding
tests, bytecode, caches, and platform metadata that is not part of the active
installation contract. Do not overwrite unrelated personal Skills.

- [ ] **Step 8: Verify the active installation**

Run quick validation and skeleton resource validation against
`C:/Users/86135/.codex/skills/build-resume-portfolio-site/`. Confirm its
`SKILL.md` contains baseline-before-structure, six category commands, and
aggregate-without-late-recommend.

- [ ] **Step 9: Report commit range and synchronization result**

Report tests, validation counts, source path, installed path, and any retained
release-packaging work that is outside this implementation plan.
