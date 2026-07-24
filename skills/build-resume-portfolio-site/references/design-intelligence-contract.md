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

## Persistence

Write the report to `.resume-site-work/reports/design-intelligence.json` using
a temporary sibling file and atomic replacement. Preserve
`selected_direction_id` through later stages. Record attempted direction IDs
when a prototype is rejected.

## Privacy

The persisted report may contain short design-query terms but never the full
resume body, name, email, phone, address, full model prompt, or font binaries.
