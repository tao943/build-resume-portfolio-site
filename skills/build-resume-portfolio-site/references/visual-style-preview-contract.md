# Visual Style Preview Contract

Preview consent can cover one category or all discovery, as stated by the user.
Record that scope in `build-state.json` as `preview_preference` (`browser`,
`text`, or `ask`) and `preview_scope` (`discovery` or `category`). Reuse explicit
ongoing consent and honor later changes. Never ask again for an already
specified preference. Preview consent does not approve design or public release.

Quick mode shows the recommended combination in one gallery. Deep mode shows
category comparisons with a neutral baseline. Both reuse the same browser URL.
The gallery is display-only evidence outside React source, not a production
fragment. Browser visits, screenshots, and reloads never select or approve.

## Create and present

Create a standalone UTF-8 document at:
`.resume-site-work/style-preview/drafts/<category-or-bundle>/<draft-id>/gallery.html`.
Use `assets/visual-companion/gallery-shell.html` for structure. Include candidate
IDs, recommended choices, approved copy, authorized local media, relevant
fit/risk/fallback notes, and an instruction to confirm in the conversation.
Do not include event collection, uploads, analytics, approval controls, or
forms. CSS motion examples must honor reduced-motion preferences.

When the user has accepted a preview, start the first session:

```sh
node "$SKILL_ROOT/scripts/visual_companion/launch.cjs" \
  --workspace-root "." --gallery "<draft-gallery-path>" --open
```

Save the returned `server_info` and full authenticated URL in build state.
For revisions and later category comparisons, update that verified session:

```sh
node "$SKILL_ROOT/scripts/visual_companion/launch.cjs" \
  --workspace-root "." --gallery "<updated-draft-gallery-path>" \
  --reuse-session "<saved-server-info-path>"
```

The launcher verifies session identity and keeps the URL and process unchanged;
it never opens another browser for reuse. Refresh the existing page. If reuse
fails, retain the last valid gallery, explain the concrete failure, and offer
the static file or a replacement session without repeatedly opening windows.
Keep immutable draft files as evidence of what was shown at each approval.

If the user declines previews, record `response: declined`,
`delivery: not-requested`, `artifact: null`. If accepted, record the returned
session gallery and `local-gallery` (or `static-fallback` when serving is
unavailable). Every enabled category in a quick bundle points to the same
session gallery. Only conversational approval advances the workflow.

Stop only the verified session using `stop.cjs --workspace-root . --server-info
<saved-server-info-path>`. Stopping preserves gallery evidence. Never expose
these private galleries publicly.
