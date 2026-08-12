# Public-Safe Design Catalog Specification

## Goal

Remove external font-service output and VPN/proxy product guidance from the
bundled design catalog so the published Skill cannot recommend or emit those
resources.

## Scope

The change is limited to `skills/build-resume-portfolio-site/` and its release
artifact. It preserves the remaining UI/UX catalog, JD matching, content
workflow, visual comparison flow, motion selection, and website generation.

## Font catalog design

- Remove the `Google Fonts URL` and `CSS Import` columns from
  `vendor/ui-ux-pro-max/data/typography.csv`, including all row values.
- Keep typography intent, pairing categories, and design notes, but replace
  unavailable web-font names and Tailwind suggestions with conservative local
  or system stacks. Chinese recommendations prefer `Microsoft YaHei`,
  `PingFang SC`, and generic `sans-serif`; general recommendations use common
  system serif, sans-serif, or monospace families.
- Remove external-font output columns and the external-font search domain from
  `vendor/ui-ux-pro-max/src/core.py`.
- Add a generation rule that typography recommendations are visual direction;
  generated sites must use local assets supplied by the user or system font
  stacks and must not add a remote font stylesheet/import.

No replacement CDN is introduced. This avoids exchanging one availability and
distribution risk for another.

## Product-template design

- Delete the `VPN & Privacy Tool` row from `products.csv`, `colors.csv`, and
  `ui-reasoning.csv`.
- Remove VPN/proxy discovery keywords from `src/core.py` so a query cannot route
  to the removed template.
- Preserve unrelated privacy, security, infrastructure, and ordinary server
  terminology when it is not product guidance for VPN/proxy operation.

## Integrity and validation

- Recompute `vendor/ui-ux-pro-max/MANIFEST.sha256` for every modified hashed
  catalog file.
- Extend release-safety tests to scan production resources for external Google
  font URLs/imports and the removed VPN/proxy product-template phrases.
- Validate the catalog schema, manifest hashes, search behavior, Skill resource
  skeleton, all repository and Skill tests, Node syntax, and Skill structure.
- Build a new versioned release directory and ZIP rather than overwriting the
  previously rejected artifact.
- Re-run the same forbidden-content and structural checks after extracting the
  ZIP. The ZIP must retain exactly one top-level Skill directory and exclude
  tests, bytecode, caches, and platform metadata.

## Acceptance criteria

1. Production Skill files contain no `fonts.google.com`,
   `fonts.googleapis.com`, remote font `@import`, or `Google Fonts URL` output
   field.
2. Production catalog and search routing contain no `VPN & Privacy Tool`, VPN
   product keyword, proxy product keyword, or server-selection product copy.
3. Typography search still returns useful pairing, mood, use case, local/system
   stack, and notes without a network dependency.
4. Catalog hashes and all validation suites pass.
5. The newly extracted release ZIP passes the same scans and structural checks.
