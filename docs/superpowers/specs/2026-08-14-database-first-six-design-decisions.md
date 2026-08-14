# Database-First Six Design Decisions

**Date:** 2026-08-14

## Goal

Move the vendored design database ahead of the six visual decisions and require
every category to retrieve evidence from the database while inheriting all
previously approved decisions. Preserve independent browser previews,
conversation-only approval, and one integrated React generation transaction.

## Constraints

- Keep the Skill self-contained and offline-capable.
- Reuse `vendor/ui-ux-pro-max` and `scripts/portfolio_design_search.py`.
- Add no dependency, cloud service, remote registry, or external runtime Skill.
- Never persist names, contact details, raw resume paragraphs, or project secrets
  in database queries or design-discovery reports.
- Do not create or edit React source during content, discovery, or planning.
- Browser previews remain independent and display-only; approval remains in the
  conversation.

## Reuse assessment

The existing adapter already validates the MIT-licensed vendored catalog,
constructs privacy-safe queries, searches BM25 domains, diversifies directions,
records source IDs, and writes reports atomically. The upstream
`nextlevelbuilder/ui-ux-pro-max-skill` repository exposes the same domain-search
core and a generic CLI, but its complete CLI and design-system persistence are
outside the competition package's approved surface.

Choose **wrapped adoption**: extend the project-owned adapter with baseline,
category, and aggregation operations. Directly adopting the upstream CLI would
produce an incompatible output shape and restore excluded resources. A
documentation-only instruction would not make per-category retrieval or
provenance mechanically verifiable.

## Workflow

### Database-first baseline

Immediately after `CONTENT_READY`, derive
`.resume-site-work/reports/content-map.json` from normalized facts and approved
copy. Before asking the first structure question, query the catalog and write:

```text
.resume-site-work/reports/design-discovery/baseline.json
```

The baseline contains exactly three materially different design directions
derived from role, industry, project domains, technology categories, content
density, authorized-media profile, explicit preferences, and visible reference
evidence. It establishes a search boundary and is not a new user approval gate.

### Category retrieval order

Each category search consumes the privacy-safe content profile, baseline, and
all earlier confirmed decisions.

| Category | Required catalog domains | Inherited context |
|---|---|---|
| `structure` | `landing`, `style`, `product`, `ux` | baseline, content density, project count |
| `typography` | `typography`, `style`, `ux` | structure, primary language, reading density |
| `color` | `color`, `style`, `ux` | structure, typography, role tone, contrast |
| `media` | `style`, `product`, `landing`, `ux` | structure, typography, color, authorized media |
| `primary_motion` | `motion`, `style`, `landing`, `ux` | all earlier decisions, content length, device constraints |
| `secondary_motion` | `motion`, `react`, `ux` | primary motion, controller ownership, performance and fallbacks |

Write one report per category:

```text
.resume-site-work/reports/design-discovery/
|-- baseline.json
|-- structure.json
|-- typography.json
|-- color.json
|-- media.json
|-- primary-motion.json
`-- secondary-motion.json
```

### Per-category transaction

For each enabled category:

1. Run the category query before presenting candidates.
2. Produce two or three materially different candidates, except secondary
   motion may expose a larger compatible set.
3. Require every database candidate to include catalog `source_ids`, fit,
   risks, trade-offs, compatibility evidence, responsive fallback, and relevant
   accessibility notes.
4. Recommend one candidate or compatible set using content fit and inherited
   decisions.
5. Ask whether to open the independent browser comparison before requesting a
   selection.
6. Receive selection and explicit approval in the conversation.
7. Lock the decision and pass it into the next category query.

No candidate without database provenance may be represented as a database
result. Reference-derived evidence remains labeled separately and has visual
priority; catalog UX, responsive, accessibility, and implementation guardrails
remain mandatory.

## Interfaces

Extend `portfolio_design_search.py` without breaking current `recommend` and
`enrich` callers.

### Baseline operation

Consumes `content-map.json` and optional reference-selection evidence. Produces
`baseline.json` with:

- privacy-safe query profile;
- three complete direction bundles;
- selected recommendation;
- guardrails and React guidelines;
- catalog version and domain provenance.

### Category operation

Consumes:

- `content-map.json`;
- `baseline.json`;
- category ID;
- zero or more previously confirmed decisions.

Produces a category report with:

- category ID and query context;
- domains searched;
- candidates and recommendation;
- inherited decision IDs;
- compatibility and fallback notes;
- source IDs and catalog version.

### Aggregate operation

After all six decisions are approved, validate and aggregate the baseline and
six category reports into the canonical
`.resume-site-work/reports/design-intelligence.json`. The generation phase
consumes this report; it must not run a new generic recommendation that could
contradict approved discovery.

## Failure handling

For each baseline or category query:

1. Search with full context.
2. If fewer than the required candidates are returned, retry once after
   removing nonessential descriptive terms while preserving approved decisions
   and engineering constraints.
3. If results remain insufficient, return `design_catalog_insufficient` with
   searched domains, queries, found source IDs, and missing candidate count.
4. Stop the category before preview or approval. Do not invent a replacement
   and do not edit React source.

An invalid catalog returns `resource_blocked`. An invalid report returns
`artifact_invalid`. Both preserve the last valid decision, preview, and
snapshot.

## State and approval

Add baseline readiness and the six discovery-report paths to build state.
Category transitions require a valid report before candidate presentation.
Browser visits, reloads, screenshots, or server events never select or approve
a candidate. A changed upstream decision invalidates its downstream category
reports, final requirements approval, and planning artifacts.

## Validation and tests

Use test-first changes. Baseline tests must fail before implementation because
the current workflow runs design search only near React generation and the
adapter has no category operation.

Required coverage:

- baseline exists before the first structure question;
- all six categories use their required domains;
- each later query contains prior approved decisions;
- every candidate has valid catalog source IDs;
- insufficient results stop without fabricated candidates;
- reference evidence and database evidence remain distinct;
- privacy-sensitive fields never reach reports;
- aggregation preserves approved candidate IDs;
- the generation stage consumes the aggregate instead of rerunning recommend;
- independent browser offers and conversation approval remain unchanged;
- discovery and planning never edit React source;
- existing recommend/enrich behavior remains compatible.

Run repository tests, the complete Skill test suite, structural validation,
resource validation, forbidden-reference scans, Node syntax checks, and
`git diff --check` before deployment.

## Non-goals

- Do not introduce cumulative visual previews.
- Do not add browser approval controls.
- Do not add a seventh user decision for the baseline.
- Do not replace the vendored design catalog.
- Do not restore remote fonts, registries, motion recipes, or provider-specific
  platform configuration.
