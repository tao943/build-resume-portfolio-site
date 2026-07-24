# Reference Library Contract

The user's visual references remain in their original workspace folder. The Skill creates a private catalog under `.resume-site-work/reference-library/` and never copies originals into the personal Skill.

## Build the catalog

```powershell
python "$SKILL_ROOT\scripts\index_reference_library.py" `
  "<reference-directory>" `
  --workspace-root "."
```

The command creates `manifest.json`, `duplicate-report.json`, normalized thumbnails, and labeled `contact-sheets/sheet-*.webp` files. Each record defaults to `license_note: "rights not verified; private style analysis only"`. A ready manifest contains stable `ref-<hash>` IDs, `path` to a thumbnail, `source_path` to the local original, dimensions, aspect tags, `source_sha256`, and `usage_scope: "style_only"`.

## Display and selection

Show contact sheets to the user with absolute local Markdown image paths. Do not display all originals inline by default. Present up to three design directions, each with one primary reference and up to two supporting references. Record the user's choice in `reports/reference-selection.json` as primary and supporting IDs.

The references are visual input only. Extract composition, color relationships, typography hierarchy, spacing density, surface language, and image treatment. Do not copy logos, text, exact compositions, branded assets, or an artist's name into an image-generation prompt.

## Image-generation boundary

Generated images may be proposed for Hero backgrounds, abstract decorative scenes, or non-factual thematic artwork after the style direction is selected. Show generated candidates with their intended slot before the style confirmation. Never invent the user's face, resume facts, client work, product screenshots, or measurable outcomes. Reference images and generated candidates remain private until the user separately authorizes publication.

## Validation

Runtime style validation reads `.resume-site-work/reference-library/manifest.json` through `--workspace-root`. Missing or empty catalogs return `resource_not_ready: reference-library`; malformed paths, missing thumbnails, and absolute traversal paths are invalid.
