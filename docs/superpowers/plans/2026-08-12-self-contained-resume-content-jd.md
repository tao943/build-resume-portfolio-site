# Self-Contained Resume Content and JD Implementation Plan

> **For agentic workers:** Execute this plan task-by-task with test-first changes and review checkpoints.

**Goal:** Make `build-resume-portfolio-site` independently turn resume material and an optional JD into an approved content handoff before generating the website.

**Architecture:** Move the minimum evidence-safe content workflow into the website Skill as bundled prompts, references, and standard-library validators. Missing or invalid handoff data routes to this internal phase. The existing approved handoff remains the boundary consumed by website generation, and a separate validated JD report preserves role matching without modifying the factual master package.

**Tech Stack:** Markdown Agent Skill, JSON contracts, Python 3 standard library, `unittest`, existing React/Vite website workflow.

## Global Constraints

- The competition artifact contains one top-level Skill and no required external Skill.
- Do not add a third-party runtime dependency, cloud service, model provider, MCP server, or remote registry.
- Keep facts, evidence, draft copy, approved copy, and JD matching separate.
- Never convert an unmatched JD requirement into a resume fact or approved claim.
- Content strategy approval and final copy approval remain separate explicit conversation gates.
- Preserve all unrelated user changes in the dirty worktree.

---

### Task 1: Define self-contained routing and release safety

**Files:**
- Modify: `skills/build-resume-portfolio-site/scripts/test_competition_release_safety.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_synced_workflow_baseline.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_validate_content_handoff.py`
- Modify: `tests/test_workflow_behavior_contract.py`

**Interfaces:**
- Consumes: current `validate_content_handoff.py` exit codes and Skill routing text.
- Produces: regression expectations for `CONTENT_PREPARATION_REQUIRED` and zero production references to `resume-content-intelligence` or `REQUIRED SUB-SKILL`.

- [ ] Add failing assertions that missing handoff returns `CONTENT_PREPARATION_REQUIRED` and names the bundled workflow.
- [ ] Add failing assertions that production Skill resources contain no external content-Skill dependency.
- [ ] Add failing assertions that the website Skill bundles content prompts, contracts, schemas, validators, and writer.
- [ ] Run the focused tests and confirm failure is caused by the missing internalized behavior.

### Task 2: Bundle the evidence-safe content workflow

**Files:**
- Create: `skills/build-resume-portfolio-site/prompts/extract-content-facts.md`
- Create: `skills/build-resume-portfolio-site/prompts/ask-content-clarification.md`
- Create: `skills/build-resume-portfolio-site/prompts/optimize-content-copy.md`
- Create/modify: content contracts, schemas, and rules under `skills/build-resume-portfolio-site/references/`
- Create/modify: extraction, normalization, validation, and handoff scripts under `skills/build-resume-portfolio-site/scripts/`
- Modify: `skills/build-resume-portfolio-site/SKILL.md`
- Modify: `skills/build-resume-portfolio-site/references/content-preflight-routing-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/artifact-layout.md`
- Modify: `skills/build-resume-portfolio-site/references/workflow-contract.md`

**Interfaces:**
- Consumes: resume/JD sources and explicit conversation approvals.
- Produces: `source-manifest.json`, `normalized-resume.json`, `approved-copy.json`, `content-provenance.json`, content design/plan reports, and optional `jd-match.json`.

- [ ] Mechanically copy the approved internal prompts, rules, schemas, and standard-library scripts from the existing content Skill.
- [ ] Adapt names and instructions so the website Skill owns preparation and repair locally.
- [ ] Change preflight exit `2` to `CONTENT_PREPARATION_REQUIRED` and provide the exact internal recovery sequence.
- [ ] Remove cross-Skill ownership language from all production resources.
- [ ] Preserve native agent reading as the primary PDF/DOCX path; make local extraction tooling a bounded optional helper with a text/transcription fallback rather than a hard dependency.
- [ ] Run the focused routing and handoff tests until green.

### Task 3: Preserve and validate JD matching

**Files:**
- Create: `skills/build-resume-portfolio-site/references/jd-match-schema.json`
- Create: `skills/build-resume-portfolio-site/scripts/validate_jd_match.py`
- Create: `skills/build-resume-portfolio-site/scripts/test_validate_jd_match.py`
- Modify: `skills/build-resume-portfolio-site/references/jd-customization-rules.md`
- Modify: `skills/build-resume-portfolio-site/references/content-package-contract.md`

**Interfaces:**
- Consumes: one structured JD report containing `requirements`, `matches`, `unmatched_requirement_ids`, `clarification_candidates`, and optional `role_specific_copy_layer_id`.
- Produces: validation errors or `OK: JD match report is valid`.

- [ ] Write tests for valid classification/matching, missing evidence on matched rows, evidence on unmatched rows, inconsistent unmatched IDs, and unsupported status/category values.
- [ ] Run tests and confirm RED because `validate_jd_match.py` is absent.
- [ ] Implement the standard-library validator and matching schema.
- [ ] Require exact JD phrases, normalized concepts, priorities, fact/evidence IDs, resume location, rationale, unmatched list, and role-specific copy metadata.
- [ ] Run JD tests until green.

### Task 4: Register and validate all bundled resources

**Files:**
- Modify: `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_validate_skill_resources.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_competition_release_safety.py`

**Interfaces:**
- Consumes: the complete website Skill directory.
- Produces: skeleton/runtime validation that fails if any internal content resource is missing.

- [ ] Add a failing test that removes each required content resource and expects resource validation failure.
- [ ] Register content preparation resources in the skeleton and discovery/content stages.
- [ ] Add platform-brand, external-sub-Skill, remote-registry, recipe, and missing-content scans to release safety.
- [ ] Run resource and release tests until green.

### Task 5: Full verification and clean competition packaging

**Files:**
- Create: a new directory under `D:/resume/submission/` without overwriting earlier packages.
- Create: a new single-Skill ZIP.

**Interfaces:**
- Consumes: verified repository Skill source.
- Produces: one clean ZIP plus SHA-256.

- [ ] Run repository tests and the complete website Skill test suite.
- [ ] Run Skill structural validation, resource validation, `git diff --check`, and Node syntax checks.
- [ ] Scan production resources for platform branding, external content-Skill references, remote registries, and removed motion recipes.
- [ ] Copy the Skill while excluding tests, bytecode, caches, and platform metadata; retain the third-party design database license, provenance, and hashes with release-safe filenames.
- [ ] Validate the release source before zipping with Python bytecode disabled.
- [ ] Create a ZIP with exactly one top-level directory, extract it, and repeat structural/resource/design-catalog/Node/forbidden-reference checks.
- [ ] Report the final ZIP path, SHA-256, verification counts, and any retained optional limitations.
