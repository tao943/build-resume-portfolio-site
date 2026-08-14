# Design Intelligence Contract

## Purpose

`design-intelligence.json` is a compact, privacy-safe design decision artifact.
It guides an LLM that still creates the React + Vite composition directly. It
is not a template, component tree, JSX payload, HTML payload, or source-code
generator.

## Inputs

Recommendation mode may use role/category, industry, project domains,
technology categories, content counts, media availability, and explicit style
preferences. It must ignore names, contact details, addresses, raw resume
paragraphs, and project/client secrets.

Enrichment mode additionally accepts an approved `StyleBrief`. Visible
reference evidence has priority over Catalog aesthetics. Catalog accessibility,
responsive, privacy, and implementation guardrails remain mandatory.

Approved-discovery mode consumes the validated database baseline, the validated
provisional anti-template baseline, all six validated category reports, and the
approved site design specification. It copies only the candidates selected in
the conversation, preserving their report paths, catalog source IDs, and
anti-template evaluations. It is the canonical generation input and cannot
recommend a different direction or reopen a decision.

## Candidate rules

- Return exactly three candidates in recommendation mode.
- Use three distinct style families.
- Every pair must differ in at least two of style family, composition, and
  surface language.
- Keep color, typography, layout, surface, and media advice coherent inside
  each candidate.
- Select the highest-fit candidate initially and retain the other two for
  explicit retry or user selection.
- Do not silently invent fixed fallback directions when the Catalog cannot
  provide three valid candidates.
- In approved-discovery mode, require every category report, require explicit
  conversational approval, and verify every selected ID exists in that report.
  A skipped media decision retains its validated report and approval but has no
  selected candidate.
- Require every category report to reference the same anti-template baseline.
  A conflicting candidate may be presented as an explicit trade-off but cannot
  be the default recommendation. Aggregation fails when the trace is missing or
  inconsistent.

## Persistence

Write the report to `.resume-site-work/reports/design-intelligence.json` using
a temporary sibling file and atomic replacement. Preserve
`selected_direction_id` through later stages. Record attempted direction IDs
when a prototype is rejected.

For integrated generation, write one `approved-discovery` aggregate from the
persisted baselines and category reports. Do not rerun `recommend`; the
aggregate preserves the exact approved IDs, selected candidate records,
discovery-report paths, anti-template evaluations, guardrails, React guidance,
and catalog provenance.

Set `anti_template_resolution_required: true`. Creative-direction compilation
must resolve every provisional rule as `adopted`, `refined`, or
`rejected_by_approved_choice`, and link that resolution to the approved category
evidence. A provisional hypothesis is never approval and cannot authorize React
source edits.

## Privacy

The persisted report may contain short design-query terms but never the full
resume body, name, email, phone, address, full model prompt, or font binaries.
