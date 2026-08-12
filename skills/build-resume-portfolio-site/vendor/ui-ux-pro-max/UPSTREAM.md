# UI/UX Pro Max upstream record

- Upstream: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- Catalog-Version: 2.11.0
- Vendored-Date: 2026-07-20
- Copyright: Copyright (c) 2024 Next Level Builder
- License: MIT

## Included

This package includes the upstream BM25 core plus the style, color,
typography, landing-page, product, reasoning, UX, motion, and React CSV data
used by the resume portfolio workflow.

## Excluded

The general CLI, design-system persistence code, remote font catalog, font
files, charts, icons, app-interface guidance, and non-React stack data are not
included.

## Local modifications

The typography data is distribution-sanitized to system font stacks and has no
remote font URL or stylesheet-import fields. The prohibited network-privacy
product template and its discovery route are removed. Portfolio-specific query construction,
privacy filtering, diversification, output contracts, and workflow integration
live outside this directory.
