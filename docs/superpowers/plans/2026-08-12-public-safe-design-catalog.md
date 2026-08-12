# Public-Safe Design Catalog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure the published Skill cannot output external Google font links/imports or VPN/proxy product guidance while preserving useful offline typography recommendations.

**Architecture:** Sanitize the vendored CSV data and search configuration at the source, then enforce the public-distribution boundary with production scans and behavioral tests. Recompute the existing catalog manifest after data changes and build a fresh single-Skill ZIP that is verified again after extraction.

**Tech Stack:** Python 3 standard library, CSV, SHA-256 manifest, `unittest`, Markdown Agent Skill, PowerShell packaging.

## Global Constraints

- Do not add a replacement CDN, remote font service, dependency, cloud service, or registry.
- Use local assets supplied by the user or conservative system font stacks.
- Remove VPN/proxy product templates and discovery routes without weakening unrelated privacy, security, infrastructure, or ordinary server terminology.
- Preserve all unrelated user changes in the dirty worktree.
- Release output contains one top-level Skill and excludes tests, bytecode, caches, and platform metadata.

---

### Task 1: Define public-distribution regression behavior

**Files:**
- Modify: `skills/build-resume-portfolio-site/scripts/test_competition_release_safety.py`
- Modify: `skills/build-resume-portfolio-site/scripts/test_installed_design_catalog.py`

**Interfaces:**
- Consumes: production files under the Skill root and `vendor/ui-ux-pro-max/src/core.py` search functions.
- Produces: failing assertions for forbidden external-font markers, removed product-template markers, and offline typography output fields.

- [ ] Add a test scanning non-test production resources for `fonts.google.com`, `fonts.googleapis.com`, remote font `@import`, and `Google Fonts URL`.
- [ ] Add a test scanning the catalog and search routing for `VPN & Privacy Tool`, VPN/proxy product keywords, and server-selection product copy.
- [ ] Add a behavioral test asserting typography search returns local/system stack information and no URL/import output keys.
- [ ] Run the focused tests and verify RED from the current catalog content and output columns.

### Task 2: Sanitize font and product catalog sources

**Files:**
- Modify: `skills/build-resume-portfolio-site/vendor/ui-ux-pro-max/data/typography.csv`
- Modify: `skills/build-resume-portfolio-site/vendor/ui-ux-pro-max/data/products.csv`
- Modify: `skills/build-resume-portfolio-site/vendor/ui-ux-pro-max/data/colors.csv`
- Modify: `skills/build-resume-portfolio-site/vendor/ui-ux-pro-max/data/ui-reasoning.csv`
- Modify: `skills/build-resume-portfolio-site/vendor/ui-ux-pro-max/src/core.py`
- Modify: `skills/build-resume-portfolio-site/vendor/ui-ux-pro-max/UPSTREAM.md`
- Modify: `skills/build-resume-portfolio-site/SKILL.md`

**Interfaces:**
- Consumes: existing CSV search columns and `_search_csv()` behavior.
- Produces: typography rows with `System Font Stack`, no network fields, no prohibited product rows, and search results incapable of emitting removed data.

- [ ] Remove the two external-font CSV columns and rewrite typography family/config values to conservative system stacks while retaining pairing intent, mood, use case, and notes.
- [ ] Remove row `157` from all three aligned product datasets without renumbering unrelated stable row IDs.
- [ ] Remove external-font output/search routing and VPN/proxy discovery keywords from `core.py`.
- [ ] Record the downstream sanitization in `UPSTREAM.md` and add the local/system-font generation invariant to `SKILL.md`.
- [ ] Run the focused tests and verify GREEN.

### Task 3: Restore catalog integrity and complete repository verification

**Files:**
- Modify: `skills/build-resume-portfolio-site/vendor/ui-ux-pro-max/MANIFEST.sha256`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_design_catalog.py` only if the sanitized schema requires it.

**Interfaces:**
- Consumes: modified catalog files.
- Produces: SHA-256 entries accepted by `validate_design_catalog.py` and a fully green repository.

- [ ] Recompute manifest hashes for every modified file already covered by `REQUIRED_HASHED_FILES`.
- [ ] Run catalog validation and correct only schema/integrity failures caused by the approved sanitization.
- [ ] Run all website Skill tests, repository tests, Skill structural validation, Node syntax checks, forbidden scans, and `git diff --check`.
- [ ] Commit the verified source changes on `codex/self-contained-resume-content-jd`.

### Task 4: Build and verify a fresh competition artifact

**Files:**
- Create: `D:/resume/submission/xfyun-2026-08-12-public-safe/build-resume-portfolio-site/`
- Create: `D:/resume/submission/build-resume-portfolio-site-xfyun-2026-08-12-public-safe.zip`

**Interfaces:**
- Consumes: verified Skill source at the committed branch head.
- Produces: a new single-top-level ZIP and SHA-256 digest.

- [ ] Copy production files while excluding `test_*.py`, `.pyc`, `__pycache__`, and platform metadata; preserve the design database license/provenance with release-safe filenames.
- [ ] Validate the release directory with bytecode disabled, including catalog hashes, Skill resources, Node syntax, and all forbidden scans.
- [ ] Zip the single top-level directory, extract it into a fresh verification directory, and repeat every release check.
- [ ] Report the ZIP path, size, file count, SHA-256, test totals, branch, and commit.
