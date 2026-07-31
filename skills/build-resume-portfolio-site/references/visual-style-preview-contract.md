# Visual Style Preview Contract

Use this display-only transaction after the user tentatively selects a
candidate for one enabled discovery category. Ask separately for every enabled category. The six supported category IDs are `structure`, `typography`,
`color`, `media`, `primary-motion`, and `secondary-motion`.

Previews are independent, not cumulative. Each preview isolates its category
against a neutral demonstration baseline. It is decision evidence, not reusable
React source and not a fragment to concatenate into the final website.

Declining one category does not suppress later preview offers. Record the
decline as `response: declined`, `delivery: not-requested`, and `artifact: null`,
then obtain the category confirmation in the conversation.

## Offer

After tentative selection, ask in a separate message whether the user wants to
open a browser for this category. Do not create the Gallery or launch a browser
before the user accepts. Consent applies only to the current category.

## Output

On acceptance, create one standalone UTF-8 document at:

```text
.resume-site-work/style-preview/drafts/<category>/<draft-id>/gallery.html
```

Use `assets/visual-companion/gallery-shell.html` as structural guidance. Show:

- the category name and question;
- all candidates, with IDs matching the design-decision candidates;
- a visual mark on the tentative selection that has no interaction semantics;
- approved resume copy and only authorized local media;
- the exact visual properties needed to judge this category;
- relevant fit, risk, mobile, accessibility, fallback, and reduced-motion notes;
- a visible instruction to return to the conversation to confirm or revise.

Structure previews compare composition and hierarchy. Typography previews
compare type and rhythm. Color previews compare color relationships. Media
previews compare media treatment. Primary- and secondary-motion previews use
small runnable samples, but contain no approval controls.

The page is display-only. Do not add forms, buttons, `data-choice`, click or
change handlers, WebSockets, event collection, uploads, analytics, or approval
controls. Browser activity never counts as selection or approval.

Do not create or modify `.resume-site-work/site` while producing a Gallery.

## Present

Resolve `SKILL_ROOT`, then run only after the user accepted the current offer:

```powershell
node "$SKILL_ROOT\scripts\visual_companion\launch.cjs" `
  --workspace-root "." `
  --gallery ".resume-site-work\style-preview\drafts\<category>\<draft-id>\gallery.html" `
  --open
```

Read the startup JSON. Give the user the complete authenticated `url` and the
absolute `gallery.html` static fallback. Automatic-open failure is non-blocking.
If Node, process lifetime, or loopback availability prevents the server, show
the standalone HTML path. Never upload or publicly expose the Gallery.

## Confirm

After display, ask the user to return to the conversation and confirm, revise,
or reject. Record the decision-level `preview` and `approval` fields in the
schema-version-3 design specification. A visit, reload, screenshot, or system
browser launch is never approval.

## Stop

Stop only the exact verified session returned by the launcher:

```powershell
node "$SKILL_ROOT\scripts\visual_companion\stop.cjs" `
  --workspace-root "." `
  --server-info "<returned-server-info-path>"
```

Stopping preserves the Gallery as discovery evidence.
