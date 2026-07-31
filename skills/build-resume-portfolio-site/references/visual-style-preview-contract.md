# Visual Style Preview Contract

Use this transaction during full site discovery after defining two or three
materially different alternatives and before writing an approved site design
specification.

## Output

Create one complete, standalone UTF-8 document at a new path:

```text
.resume-site-work/style-preview/drafts/<draft-id>/gallery.html
```

Use `assets/visual-companion/gallery-shell.html` as structural guidance. The
gallery contains:

- two or three directions with IDs matching `alternatives`;
- approved resume copy and only authorized local media;
- visual protagonist, composition, typography, color, density, and hierarchy;
- representative interaction state shown visually without executable control;
- desktop framing and a compact/mobile frame when responsive behavior differs;
- fit, risk, and responsive trade-offs for each direction;
- a visible instruction to return to the conversation to select and approve.

The page is display-only. Do not add forms, buttons, `data-choice`, WebSockets,
event collection, uploads, analytics, or approval controls. Browser activity
never counts as selection or approval.

Do not create or modify `.resume-site-work/site` while producing the gallery.

## Present

Resolve `SKILL_ROOT` to this Skill directory, then run:

```powershell
node "$SKILL_ROOT\scripts\visual_companion\launch.cjs" `
  --workspace-root "." `
  --gallery ".resume-site-work\style-preview\drafts\<draft-id>\gallery.html" `
  --open
```

Read the single startup JSON object. Give the user both:

- the complete authenticated `url`, including its query string;
- the absolute generated `gallery.html` path as the static fallback.

Automatic opening is best effort. `open_warning: "OPEN_FAILED"` leaves the
server valid; show the URL. If Node is unavailable, launch fails, the process
is reaped, or loopback is unreachable, show the standalone HTML path. In a
remote environment, use only an existing user-authorized port-forwarding
mechanism; do not publish or upload the gallery.

Process lifetime differs by host. Keep `launch.cjs --foreground` alive through
the host's asynchronous shell facility when detached processes are reaped.

## Approve

Ask the user to name a candidate in the conversation. After the reply:

1. Record the chosen candidate in `selected_alternative_id` and
   `visual_preview.selected_candidate_id`.
2. Set `approval_channel` to `conversation`.
3. Set `explicitly_approved` to `true` only after an explicit conversational
   approval.
4. Write schema-version-2 `reports/site-design-spec.json`.
5. Validate it before writing the implementation plan.

A browser visit, reload, screenshot, or system-browser launch is not approval.

## Stop

Stop only the exact verified session from the returned `server_info`:

```powershell
node "$SKILL_ROOT\scripts\visual_companion\stop.cjs" `
  --workspace-root "." `
  --server-info "<returned-server-info-path>"
```

Stopping preserves the session gallery. Draft and session artifacts are
discovery evidence, not React source, confirmed snapshots, or publishable
output.
