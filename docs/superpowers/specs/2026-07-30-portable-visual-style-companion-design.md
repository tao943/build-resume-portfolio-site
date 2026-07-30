# Portable Visual Style Companion Design

## Objective

Integrate a self-contained, cross-platform visual style preview into the
`build-resume-portfolio-site` Skill. During full site discovery, the Skill
must be able to show two or three materially different visual directions in
the user's normal browser without depending on the Codex Browser plugin,
another installed Skill, an MCP server, or an npm install.

The browser is display-only. A click, page visit, or browser-side action never
counts as approval. The user must select and approve a direction explicitly in
the conversation.

## Scope

This change adds a local visual gallery and integrates it into the existing
site-design approval gate. It does not:

- automate or inspect the browser;
- collect browser events or form submissions;
- build multiple production React applications;
- upload resume content or preview artifacts;
- add an MCP server;
- change the content-verification workflow;
- replace the final React, build, screenshot, or confirmation stages.

## User Experience

For a new site or a material visual-direction change:

1. The Skill completes content preflight and decision-bearing discovery.
2. It defines two or three materially different candidate directions.
3. It creates a display-only HTML gallery using approved resume content.
4. It starts a loopback-only local preview server and attempts to open the
   system browser.
5. It also prints the complete authenticated URL in the conversation.
6. The user reviews the candidates and replies in the conversation.
7. The Skill records the selected candidate and explicit conversational
   approval in `site-design-spec.json`.
8. Only then may it create and validate the implementation plan.

If the browser cannot be opened automatically, the user can click the URL. If
the server cannot remain alive, the Skill provides the generated static HTML
file as a fallback. The conversation remains the only approval channel in
every case.

## Architecture

### Skill workflow

`resume-portfolio-workflow` continues to route `site-full` work and does not
run the preview server itself.

`build-resume-portfolio-site` owns a new visual-preview transaction inside the
discovery gate:

```text
candidate definitions
-> display-only gallery
-> local preview
-> conversational selection
-> validated design specification
-> explicit conversational approval
-> implementation plan
```

Preview artifacts live under:

```text
.resume-site-work/style-preview/
  sessions/<session-id>/
    gallery.html
    assets/
    state/
      server-info.json
      server.pid
```

They are discovery artifacts, not React source, confirmed snapshots, or
publishable site output.

### Portable launcher

The launcher is a CommonJS Node program so Windows, macOS, and Linux agents can
invoke the same command:

```text
node <skill-root>/scripts/visual_companion/launch.cjs \
  --workspace-root <workspace> \
  [--open] [--foreground]
```

It:

- requires only Node built-in modules;
- allocates a random high port unless an explicit port is supplied;
- binds to `127.0.0.1` by default;
- creates a random per-session key;
- writes one JSON startup record to stdout and `server-info.json`;
- launches the system browser with argument-safe platform commands when
  `--open` is requested;
- supports foreground execution for agents that reap detached processes;
- reports failures as stable JSON error categories.

The stop command accepts an exact session directory or server-info path,
validates that the resolved target is inside
`.resume-site-work/style-preview/sessions`, and terminates only the recorded
process.

### Read-only server

The server exposes only authenticated `GET` and `HEAD` requests. It rejects
write methods and paths outside the active session directory.

The bootstrap URL contains `?key=<random-token>`. On first load, the server
stores the key in a same-site, HTTP-only cookie so gallery assets can load
without exposing the token to page scripts.

Security headers include:

- `Cache-Control: no-store`;
- `Content-Security-Policy` suitable for local static assets;
- `X-Content-Type-Options: nosniff`;
- `X-Frame-Options: DENY`;
- `Referrer-Policy: no-referrer`;
- `Cross-Origin-Resource-Policy: same-origin`.

The server has no WebSocket endpoint, event log, form endpoint, upload route,
directory listing, proxy, or arbitrary filesystem access.

### Gallery document

The Skill writes a complete `gallery.html` using a bundled shell as structural
guidance. The generated gallery:

- contains two or three candidate directions;
- uses approved copy and authorized local assets where they materially affect
  the judgment;
- gives each candidate a stable ID matching the design specification;
- shows the visual protagonist, composition, typography, color, density, and
  one representative interaction state;
- includes desktop and compact/mobile framing where responsive behavior
  distinguishes candidates;
- contains no selection controls or approval buttons;
- states prominently that approval must be given in the conversation;
- works as a standalone `file:` document when server startup fails.

Candidate previews may use HTML and CSS mockups, inline SVG, or local raster
assets. They must not create or modify `.resume-site-work/site`.

## Design Specification Changes

`site-design-spec.json` gains a required `visual_preview` object for full site
design work:

```json
{
  "visual_preview": {
    "mode": "local-gallery",
    "artifact": ".resume-site-work/style-preview/sessions/<id>/gallery.html",
    "candidate_ids": ["direction-a", "direction-b"],
    "recommended_candidate_id": "direction-b",
    "selected_candidate_id": "direction-b",
    "approval_channel": "conversation",
    "explicitly_approved": true
  }
}
```

The validator enforces:

- two or three unique candidate IDs;
- recommendation and selection belong to the candidate set;
- `approval_channel` equals `conversation`;
- the gallery artifact remains under the style-preview directory;
- implementation planning cannot proceed while
  `explicitly_approved` is false.

The active site-design specification schema advances from version 1 to version
2. Full-workflow version-2 specifications require `visual_preview`;
fast-change specifications may omit it because they preserve an already
approved visual direction. Version-1 specifications are rejected and must
return to discovery rather than being migrated or treated as implicitly
approved. The repository fixture advances to version 2 with a valid local
gallery record.

## Agent Compatibility

The Skill documents one portable command and environment-specific process
lifetime guidance:

- Codex: use a yielded or persistent foreground command;
- Claude Code and Cursor: use their background shell facility;
- Copilot CLI: use an asynchronous shell;
- other local coding agents: keep the foreground process alive or provide the
  static HTML fallback;
- remote/container agents: report that loopback may be inaccessible and use
  an existing user-authorized port-forwarding mechanism when available.

The implementation does not claim compatibility with agents that lack shell
execution, filesystem access, Node.js, and a route from the user browser to the
served host.

## Error Handling

Failures are isolated from confirmed artifacts and workflow state:

- `NODE_UNAVAILABLE`: provide the static HTML artifact.
- `PORT_BIND_FAILED`: retry a bounded number of random ports, then fall back.
- `OPEN_FAILED`: keep the server active and provide the URL.
- `SERVER_REAPED`: provide the static HTML artifact and process-lifetime
  instructions.
- `UNREACHABLE_REMOTE`: retain the artifact and request an existing
  user-authorized port-forwarding route.
- `INVALID_PREVIEW_PATH`: stop without serving files.

No failure may create React source, mark a design approved, advance the build
stage, or replace the current preview.

## Testing

Automated tests cover:

- startup JSON and server-info generation;
- authenticated gallery access;
- rejection of missing or incorrect keys;
- `GET` and `HEAD` behavior;
- rejection of write methods and traversal attempts;
- local-asset MIME types and security headers;
- loopback default binding;
- argument-safe browser launcher selection;
- automatic-open failure isolation;
- foreground lifecycle and exact-session stop behavior;
- standalone gallery fallback;
- validator acceptance of a valid conversational approval;
- validator rejection of browser-derived or missing approval;
- Skill behavior contract text and packaged-resource presence.

A manual smoke test starts the server against a temporary workspace, opens the
gallery URL, verifies desktop and mobile browser rendering, stops the exact
session, and confirms that no production site or confirmed artifact changed.

## Distribution

All runtime files ship inside the plugin's
`skills/build-resume-portfolio-site` directory. The Skill resolves them from
its own `SKILL_ROOT`; it never references a user's global Codex Skill folder or
the external `brainstorming` Skill.

Before publishing, validate the plugin and installed-copy behavior. The new
implementation will be original and minimal rather than copying the existing
Visual Companion source.
