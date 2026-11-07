# Printable resume and PDF delivery

Use this when delivering a completed portfolio or updating approved resume copy.
The website and downloadable resume must use the same approved content package.
Export is local; it does not publish the website.

## Select content, preserve approval

Run the normal content handoff validator first. The exporter runs it again,
including exact comparison with the reviewed copy. Use only `approved_copy`
block IDs for the name/title, contact lines, and section text. If a name or
contact item exists only in raw facts, add it to the content review and obtain
copy approval before export. Never copy the full normalized resume into a PDF.

Create `reports/resume-export.json` from the approved package. This is a layout
selection, not a second resume data format. It cannot introduce new wording.
Get the current canonical package digest with:

```sh
"$PYTHON" "$SKILL_ROOT/scripts/export_resume.py" \
  --workspace-root . --package-hash
```

Example plan (replace IDs with actual approved blocks; use the printed digest):

```json
{
  "schema_version": 1,
  "package_revision": 1,
  "package_sha256": "<digest of current approved package>",
  "language": "zh",
  "audience": "private",
  "title_block_id": "name",
  "contact_block_ids": ["contact"],
  "sections": [
    {"kind": "summary", "block_ids": ["summary"]},
    {"kind": "work", "block_ids": ["work-introduction", "work-result"]},
    {"kind": "projects", "block_ids": ["project-one"]}
  ]
}
```

`language` is `zh` or `en` and controls section labels; it never translates
approved wording. Section kinds are `summary`, `work`, `projects`, `education`,
`skills`, and `links`. Omit absent sections. Every chosen block appears once.
Dates, employers, roles, names, and URLs belong in approved blocks just like
other resume text. Long documents paginate automatically instead of shrinking
to unreadable text. A content revision or wording change invalidates the plan
digest; regenerate the plan from the new approved package.

For a downloadable website resume, set `audience` to `public` and include:

```json
"public_approval": {
  "status": "user_approved",
  "source": "conversation",
  "evidence_quote": "<the user's existing approval covering these public fields>",
  "block_ids": ["name", "contact", "summary", "work-introduction", "work-result", "project-one"]
}
```

The IDs must exactly cover the selected blocks. Reuse existing explicit public
scope approval when it covers these fields; do not ask again unnecessarily.
General wording approval alone does not authorize publishing private contacts.
Keep a private application PDF separate if it contains extra contact details.

## Generate and inspect

```sh
"$PYTHON" "$SKILL_ROOT/scripts/export_resume.py" \
  --workspace-root . \
  --plan .resume-site-work/reports/resume-export.json \
  --output-dir .resume-site-work/exports/resume-v1
```

This writes `resume.pdf`, `resume.html`, and a private `export-report.json`.
PDF export requires `reportlab` and `pypdf` in the selected Python environment.
Use the environment checker before generation. If dependencies are missing,
install them in a project environment or use `--format html` to retain a
printable HTML file; do not call that fallback a completed PDF delivery.
The command refuses an existing output directory and stages outputs before
promotion. Use a new revision directory on updates. For an immutable saved
job version, pass its snapshot workspace as `--workspace-root`.

The PDF is single-column A4 with selectable text and clickable visible HTTP(S)
and `mailto:` URLs. The script re-extracts its text, checks that all approved
wording survives in order, and records page count. These checks do not prove
compatibility with every ATS or replace visual inspection. For Chinese and
other non-Latin text the exporter locates a local TrueType font, verifies its
glyph coverage, and embeds the subset in the PDF. It checks common macOS,
Windows, and Linux font paths. If none cover the approved text, supply
`--font /path/to/Chinese-capable.ttf` (TrueType `.ttc` is also accepted) or use
HTML. No font is downloaded automatically and missing glyphs are never silently
substituted. Any wording change to avoid an unsupported character requires
the normal content approval.

Render every PDF page using an available local renderer (for example
`pdftoppm -png resume.pdf resume-page`), inspect Chinese glyphs, pagination,
links, clipping, and spacing, and record the actual review. Keep the previous
valid export on any failure. Do not report visual checks as passed solely
because text extraction succeeded.

## Website download and updates

After the public PDF passes review, copy only `resume.pdf` into
`.resume-site-work/site/public/resume.pdf` and add a visible download link.
Use the site's base path (`import.meta.env.BASE_URL` in Vite) so a subdirectory
build still resolves the PDF. Verify the link against the built preview and
confirm that the served bytes match the exported PDF hash. Do not copy the
export plan, report, evidence, or private PDF into public source/output.

Changing approved copy requires a fresh export and replacement of the
downloadable file in the same revision as the website content. Report the
selected job version, actual PDF checks, and file paths at delivery. No hosting
or deployment workflow is added by this contract.
