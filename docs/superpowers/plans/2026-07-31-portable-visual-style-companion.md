# Portable Visual Style Companion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dependency-free, cross-platform, display-only local visual gallery to the website-design approval gate.

**Architecture:** A small CommonJS server serves one generated gallery from a token-protected loopback URL. Cross-platform launch and stop commands manage exact session directories, while the Skill contract and site-design schema require the user to approve a displayed candidate in the conversation before implementation planning.

**Tech Stack:** Node.js built-in modules, Python 3 standard library, JSON Schema documentation, Python `unittest`.

## Global Constraints

- Use only Node.js built-in modules; do not require `npm install`.
- Bind to `127.0.0.1` by default and authenticate every request with a random session key.
- Accept only `GET` and `HEAD`; do not add WebSockets, forms, uploads, proxies, or browser event collection.
- Treat the browser as display-only; approval is valid only when `approval_channel` is `conversation`.
- Keep generated galleries under `.resume-site-work/style-preview/sessions/`.
- Never create or edit `.resume-site-work/site` during visual style comparison.
- Preserve a standalone `gallery.html` fallback when automatic opening or server lifetime fails.
- Implement original minimal code; do not copy the external Brainstorming Visual Companion.
- Advance full site-design specifications to schema version 2; do not infer or migrate approval from version 1.

## File Map

- Create `skills/build-resume-portfolio-site/scripts/visual_companion/server.cjs`: authenticated read-only static server.
- Create `skills/build-resume-portfolio-site/scripts/visual_companion/launch.cjs`: session creation, server lifecycle, and optional system-browser launch.
- Create `skills/build-resume-portfolio-site/scripts/visual_companion/stop.cjs`: exact-session process termination with path containment checks.
- Create `skills/build-resume-portfolio-site/assets/visual-companion/gallery-shell.html`: standalone display-only gallery starting point.
- Create `skills/build-resume-portfolio-site/references/visual-style-preview-contract.md`: agent-facing generation and fallback protocol.
- Create `tests/test_visual_companion.py`: process, HTTP, security, fallback, and stop tests.
- Modify `skills/build-resume-portfolio-site/references/site-design-spec-schema.json`: document schema version 2 and `visual_preview`.
- Modify `skills/build-resume-portfolio-site/scripts/validate_site_design_spec.py`: enforce conversational approval and gallery containment.
- Modify `tests/fixtures/site-design-spec-valid.json`: valid version-2 full-workflow fixture.
- Modify `tests/test_workflow_behavior_contract.py`: rejection cases for missing or browser-derived approval.
- Modify `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`: package and discovery-resource checks.
- Modify `skills/build-resume-portfolio-site/SKILL.md`: insert visual-preview transaction before site-design approval.
- Modify `skills/build-resume-portfolio-site/references/site-brainstorming-contract.md`: require display of two or three directions.
- Modify `skills/build-resume-portfolio-site/references/artifact-layout.md`: record style-preview ownership and lifecycle.
- Modify `README.md`: document dependency-free browser presentation and conversational approval.

---

### Task 1: Enforce the Version-2 Visual Preview Approval Contract

**Files:**

- Modify: `tests/fixtures/site-design-spec-valid.json`
- Modify: `tests/test_workflow_behavior_contract.py`
- Modify: `skills/build-resume-portfolio-site/references/site-design-spec-schema.json`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_site_design_spec.py`

**Interfaces:**

- Consumes: existing `validate(payload: Any) -> list[str]`.
- Produces: version-2 `visual_preview` with candidate IDs aligned to `alternatives`.

- [ ] **Step 1: Add failing validator tests**

Add a valid fixture field:

```json
"visual_preview": {
  "mode": "local-gallery",
  "artifact": ".resume-site-work/style-preview/sessions/style-1/gallery.html",
  "candidate_ids": ["editorial", "cinematic"],
  "recommended_candidate_id": "editorial",
  "selected_candidate_id": "editorial",
  "approval_channel": "conversation",
  "explicitly_approved": true
}
```

Change `schema_version` to `2`, then add tests:

```python
def test_full_site_requires_visual_preview(self) -> None:
    result = self.run_validator(
        "build-resume-portfolio-site",
        "validate_site_design_spec.py",
        "site-design-spec-valid.json",
        lambda payload: payload.pop("visual_preview"),
    )
    self.assertNotEqual(result.returncode, 0)

def test_browser_activity_cannot_approve_site_design(self) -> None:
    result = self.run_validator(
        "build-resume-portfolio-site",
        "validate_site_design_spec.py",
        "site-design-spec-valid.json",
        lambda payload: payload["visual_preview"].update(
            {"approval_channel": "browser"}
        ),
    )
    self.assertNotEqual(result.returncode, 0)

def test_version_one_site_design_is_rejected(self) -> None:
    result = self.run_validator(
        "build-resume-portfolio-site",
        "validate_site_design_spec.py",
        "site-design-spec-valid.json",
        lambda payload: payload.update({"schema_version": 1}),
    )
    self.assertNotEqual(result.returncode, 0)
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```powershell
python -m unittest tests.test_workflow_behavior_contract -v
```

Expected: the new version-2 fixture or rejection tests fail because the validator still accepts schema version 1 and ignores `visual_preview`.

- [ ] **Step 3: Implement version-2 validation**

Add `visual_preview` to the schema documentation and validate it only when
`workflow_mode == "full"`:

```python
def _validate_visual_preview(
    preview: Any,
    alternative_ids: list[str],
) -> list[str]:
    if not isinstance(preview, dict):
        return ["full mode requires visual_preview"]
    required = {
        "mode",
        "artifact",
        "candidate_ids",
        "recommended_candidate_id",
        "selected_candidate_id",
        "approval_channel",
        "explicitly_approved",
    }
    errors = [
        f"visual_preview missing field: {name}"
        for name in sorted(required - set(preview))
    ]
    if errors:
        return errors
    candidate_ids = preview["candidate_ids"]
    if (
        not isinstance(candidate_ids, list)
        or not 2 <= len(candidate_ids) <= 3
        or not all(isinstance(item, str) and item.strip() for item in candidate_ids)
        or len(candidate_ids) != len(set(candidate_ids))
    ):
        errors.append("visual_preview candidate_ids must contain two or three unique IDs")
        candidate_ids = []
    if set(candidate_ids) != set(alternative_ids):
        errors.append("visual_preview candidate_ids must match alternatives")
    if preview["mode"] != "local-gallery":
        errors.append("visual_preview mode must be local-gallery")
    artifact = str(preview["artifact"]).replace("\\", "/")
    prefix = ".resume-site-work/style-preview/sessions/"
    if not artifact.startswith(prefix) or not artifact.endswith("/gallery.html"):
        errors.append("visual_preview artifact must be a session gallery")
    for key in ("recommended_candidate_id", "selected_candidate_id"):
        if preview[key] not in candidate_ids:
            errors.append(f"visual_preview {key} must reference a candidate")
    if preview["approval_channel"] != "conversation":
        errors.append("visual_preview approval_channel must be conversation")
    if preview["explicitly_approved"] is not True:
        errors.append("visual_preview must be explicitly approved")
    return errors
```

Set the active schema constant to `2`, call this helper after collecting
alternative IDs, and keep fast-change mode exempt from the preview object.

- [ ] **Step 4: Run tests and verify success**

Run:

```powershell
python -m unittest tests.test_workflow_behavior_contract -v
python skills/build-resume-portfolio-site/scripts/validate_site_design_spec.py tests/fixtures/site-design-spec-valid.json
```

Expected: all behavior tests pass and the validator prints
`OK: site design spec is valid`.

- [ ] **Step 5: Commit**

```powershell
git add -- tests/fixtures/site-design-spec-valid.json tests/test_workflow_behavior_contract.py skills/build-resume-portfolio-site/references/site-design-spec-schema.json skills/build-resume-portfolio-site/scripts/validate_site_design_spec.py
git commit -m "feat: require conversational visual preview approval"
```

### Task 2: Build the Authenticated Read-Only Gallery Server

**Files:**

- Create: `tests/test_visual_companion.py`
- Create: `skills/build-resume-portfolio-site/scripts/visual_companion/server.cjs`

**Interfaces:**

- Consumes: `--session-dir`, `--gallery`, optional `--host`, `--port`, and `--token`.
- Produces: one-line JSON `{type, pid, port, host, url, session_dir, gallery}` and an HTTP server that serves only the session gallery and assets.

- [ ] **Step 1: Add failing HTTP and security tests**

Create a test harness that starts Node, reads the first stdout line, and uses
`urllib.request`:

```python
class VisualCompanionServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.session = Path(self.temp.name)
        self.gallery = self.session / "gallery.html"
        self.gallery.write_text("<!doctype html><h1>Directions</h1>", encoding="utf-8")
        command = [
            "node",
            str(SERVER),
            "--session-dir", str(self.session),
            "--gallery", str(self.gallery),
            "--port", "0",
            "--token", "test-token-1234567890",
        ]
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.info = json.loads(self.process.stdout.readline())

    def tearDown(self) -> None:
        self.process.terminate()
        self.process.wait(timeout=5)
        self.temp.cleanup()

    def test_authenticated_get_serves_gallery(self) -> None:
        with urllib.request.urlopen(self.info["url"], timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"Directions", response.read())
            self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_missing_key_is_forbidden(self) -> None:
        url = f'http://127.0.0.1:{self.info["port"]}/'
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(url, timeout=3)
        self.assertEqual(caught.exception.code, 403)

    def test_post_is_rejected(self) -> None:
        request = urllib.request.Request(
            self.info["url"], data=b"x", method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 405)
```

Add tests for `HEAD`, wrong keys, traversal, unsupported extensions, loopback
default binding, and all required security headers.

- [ ] **Step 2: Run the server tests and verify failure**

Run:

```powershell
python -m unittest tests.test_visual_companion -v
```

Expected: FAIL because `server.cjs` does not exist.

- [ ] **Step 3: Implement the minimal server**

Implement argument parsing, canonical path containment, constant-time token
comparison, MIME lookup, `GET`/`HEAD`, and startup JSON using:

```javascript
const crypto = require("crypto");
const fs = require("fs");
const http = require("http");
const path = require("path");

const MIME = new Map([
  [".html", "text/html; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".js", "application/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".svg", "image/svg+xml"],
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".webp", "image/webp"],
  [".gif", "image/gif"],
]);

function safeEqual(left, right) {
  const a = Buffer.from(String(left));
  const b = Buffer.from(String(right));
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

function inside(root, target) {
  const relative = path.relative(root, target);
  return relative === "" || (
    !relative.startsWith(`..${path.sep}`) &&
    relative !== ".." &&
    !path.isAbsolute(relative)
  );
}
```

Reject symlinks and non-regular files, emit stable JSON errors to stderr, set
the authentication cookie after a valid query-key request, and close cleanly
on `SIGINT` or `SIGTERM`.

- [ ] **Step 4: Run tests and syntax checks**

Run:

```powershell
node --check skills/build-resume-portfolio-site/scripts/visual_companion/server.cjs
python -m unittest tests.test_visual_companion.VisualCompanionServerTests -v
```

Expected: Node syntax check exits `0`; all server tests pass.

- [ ] **Step 5: Commit**

```powershell
git add -- tests/test_visual_companion.py skills/build-resume-portfolio-site/scripts/visual_companion/server.cjs
git commit -m "feat: add read-only visual gallery server"
```

### Task 3: Add Cross-Platform Launch and Exact-Session Stop Commands

**Files:**

- Modify: `tests/test_visual_companion.py`
- Create: `skills/build-resume-portfolio-site/scripts/visual_companion/launch.cjs`
- Create: `skills/build-resume-portfolio-site/scripts/visual_companion/stop.cjs`

**Interfaces:**

- Consumes: `launch.cjs --workspace-root <path> --gallery <path> [--open] [--foreground]`.
- Produces: startup JSON containing `server_info` and
  `.resume-site-work/style-preview/sessions/<id>/state/server-info.json`.
- Consumes: `stop.cjs --workspace-root <path> --server-info <path>`.
- Produces: JSON `{type:"server-stopped", pid, session_dir}` without deleting artifacts.

- [ ] **Step 1: Add failing lifecycle tests**

Add tests that:

```python
def test_launch_creates_contained_session_and_server_info(self) -> None:
    result = self.launch()
    info = json.loads(result.stdout.splitlines()[0])
    session = Path(info["session_dir"]).resolve()
    expected = (
        self.workspace
        / ".resume-site-work"
        / "style-preview"
        / "sessions"
    ).resolve()
    self.assertTrue(session.is_relative_to(expected))
    self.assertTrue((session / "state" / "server-info.json").is_file())

def test_open_failure_does_not_stop_server(self) -> None:
    result = self.launch(
        extra_env={"VISUAL_COMPANION_OPEN_COMMAND": "__missing_command__"},
        open_browser=True,
    )
    info = json.loads(result.stdout.splitlines()[0])
    with urllib.request.urlopen(info["url"], timeout=3) as response:
        self.assertEqual(response.status, 200)

def test_stop_rejects_server_info_outside_workspace(self) -> None:
    result = subprocess.run(
        [
            "node", str(STOP),
            "--workspace-root", str(self.workspace),
            "--server-info", str(self.workspace / "outside.json"),
        ],
        capture_output=True, text=True, check=False,
    )
    self.assertNotEqual(result.returncode, 0)
```

Also assert that stop terminates the recorded process and preserves
`gallery.html`.

- [ ] **Step 2: Run lifecycle tests and verify failure**

Run:

```powershell
python -m unittest tests.test_visual_companion.VisualCompanionLifecycleTests -v
```

Expected: FAIL because launch and stop commands do not exist.

- [ ] **Step 3: Implement launch and browser-open isolation**

Use `spawn` with argument arrays and platform launchers:

```javascript
function browserCommand(url) {
  if (process.env.VISUAL_COMPANION_OPEN_COMMAND) {
    return {
      command: process.env.VISUAL_COMPANION_OPEN_COMMAND,
      args: [url],
    };
  }
  if (process.platform === "win32") {
    return {
      command: "powershell.exe",
      args: [
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        "Start-Process -FilePath $args[0]",
        url,
      ],
    };
  }
  if (process.platform === "darwin") return {command: "open", args: [url]};
  return {command: "xdg-open", args: [url]};
}
```

Create the session with `fs.mkdtempSync`, copy the supplied gallery and its
optional `assets` sibling into it, generate a 32-byte token, and pass the token
to `server.cjs`. Write server info atomically using a temporary file plus
`renameSync`.

Foreground mode inherits server lifetime. Default mode detaches the child,
waits for its startup JSON, persists server info, and exits. An open failure
adds an `open_warning` to startup output but does not stop the server.

- [ ] **Step 4: Implement exact-session stop**

Resolve the workspace sessions root and server-info path, require containment,
parse an integer PID, and call `process.kill(pid, "SIGTERM")`. Refuse missing,
malformed, outside-root, or PID-mismatched records. Do not delete the session.

- [ ] **Step 5: Run lifecycle and syntax tests**

Run:

```powershell
node --check skills/build-resume-portfolio-site/scripts/visual_companion/launch.cjs
node --check skills/build-resume-portfolio-site/scripts/visual_companion/stop.cjs
python -m unittest tests.test_visual_companion -v
```

Expected: all syntax and lifecycle checks pass.

- [ ] **Step 6: Commit**

```powershell
git add -- tests/test_visual_companion.py skills/build-resume-portfolio-site/scripts/visual_companion/launch.cjs skills/build-resume-portfolio-site/scripts/visual_companion/stop.cjs
git commit -m "feat: manage portable visual preview sessions"
```

### Task 4: Package the Display-Only Gallery and Validate Its Resources

**Files:**

- Create: `skills/build-resume-portfolio-site/assets/visual-companion/gallery-shell.html`
- Create: `skills/build-resume-portfolio-site/references/visual-style-preview-contract.md`
- Modify: `skills/build-resume-portfolio-site/scripts/validate_skill_resources.py`
- Modify: `tests/test_workflow_behavior_contract.py`
- Modify: `tests/test_visual_companion.py`

**Interfaces:**

- Consumes: approved copy, authorized local media, and two or three alternative IDs.
- Produces: standalone `gallery.html` with no controls, forms, or approval semantics.

- [ ] **Step 1: Add failing package and static fallback tests**

Add:

```python
def test_visual_companion_resources_are_packaged(self) -> None:
    root = ROOT / "skills" / "build-resume-portfolio-site"
    required = (
        "assets/visual-companion/gallery-shell.html",
        "references/visual-style-preview-contract.md",
        "scripts/visual_companion/server.cjs",
        "scripts/visual_companion/launch.cjs",
        "scripts/visual_companion/stop.cjs",
    )
    for relative in required:
        self.assertTrue((root / relative).is_file(), relative)

def test_gallery_shell_is_display_only(self) -> None:
    text = GALLERY_SHELL.read_text(encoding="utf-8").lower()
    self.assertNotIn("<form", text)
    self.assertNotIn("data-choice", text)
    self.assertIn("approve in the conversation", text)
```

Run the skeleton resource validator in a temporary copied Skill with each new
resource removed once and assert `missing_contract` or
`missing_visual_companion` is reported.

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
python -m unittest tests.test_visual_companion tests.test_workflow_behavior_contract -v
```

Expected: resource and gallery-shell tests fail.

- [ ] **Step 3: Add the gallery shell and preview contract**

Create a responsive shell containing:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Portfolio visual directions</title>
  <style>
    :root { color-scheme: light dark; font-family: system-ui, sans-serif; }
    body { margin: 0; background: #111; color: #f5f5f5; }
    main { width: min(1440px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 64px; }
    .directions { display: grid; gap: 24px; }
    .direction { border: 1px solid #444; border-radius: 18px; overflow: hidden; }
    .notice { padding: 14px 18px; background: #f0cf5b; color: #18140a; }
    @media (max-width: 720px) { main { width: min(100% - 20px, 1440px); } }
  </style>
</head>
<body>
  <p class="notice">Review the directions here, then approve in the conversation.</p>
  <main>
    <!-- Replace this comment with two or three complete direction sections. -->
  </main>
</body>
</html>
```

The contract must define candidate IDs, real-content use, desktop/mobile
framing, no browser approval, server commands, static fallback, process
lifetime by agent class, and cleanup.

- [ ] **Step 4: Register discovery resources**

Add these resources:

```python
CONTRACT_SPECS.update({
    "visual-style-preview-contract":
        "references/visual-style-preview-contract.md",
})

VISUAL_COMPANION_FILES = (
    "assets/visual-companion/gallery-shell.html",
    "scripts/visual_companion/server.cjs",
    "scripts/visual_companion/launch.cjs",
    "scripts/visual_companion/stop.cjs",
)
```

Include the contract and files in `discovery` and `skeleton` validation.
Return `missing_visual_companion: <relative-path>` for absent files.

- [ ] **Step 5: Run resource and standalone rendering tests**

Run:

```powershell
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode skeleton
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --stage discovery
python -m unittest tests.test_visual_companion tests.test_workflow_behavior_contract -v
```

Expected: both resource reports have `"ok": true`; tests pass.

- [ ] **Step 6: Commit**

```powershell
git add -- skills/build-resume-portfolio-site/assets/visual-companion/gallery-shell.html skills/build-resume-portfolio-site/references/visual-style-preview-contract.md skills/build-resume-portfolio-site/scripts/validate_skill_resources.py tests/test_visual_companion.py tests/test_workflow_behavior_contract.py
git commit -m "feat: package display-only style gallery"
```

### Task 5: Integrate the Preview Transaction into the Skill Workflow

**Files:**

- Modify: `skills/build-resume-portfolio-site/SKILL.md`
- Modify: `skills/build-resume-portfolio-site/references/site-brainstorming-contract.md`
- Modify: `skills/build-resume-portfolio-site/references/artifact-layout.md`
- Modify: `README.md`
- Modify: `tests/test_workflow_behavior_contract.py`

**Interfaces:**

- Consumes: validated discovery resources and candidate alternatives.
- Produces: displayed gallery plus conversation-approved version-2 site design spec.

- [ ] **Step 1: Add failing workflow text tests**

Add:

```python
def test_site_discovery_requires_display_only_visual_gallery(self) -> None:
    text = self.read_skill("build-resume-portfolio-site").lower()
    self.assertIn("visual-style-preview-contract.md", text)
    self.assertIn("approval remains in the conversation", text)
    self.assertIn("launch.cjs", text)
    self.assertIn("do not edit react source", text)

def test_browser_activity_never_counts_as_approval(self) -> None:
    contract = (
        ROOT / "skills" / "build-resume-portfolio-site"
        / "references" / "site-brainstorming-contract.md"
    ).read_text(encoding="utf-8").lower()
    self.assertIn("browser activity never counts as approval", contract)
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
python -m unittest tests.test_workflow_behavior_contract -v
```

Expected: the new workflow wording tests fail.

- [ ] **Step 3: Update the discovery sequence**

In `SKILL.md`, require:

```text
candidate alternatives
-> gallery.html generated outside site/
-> launch.cjs invoked with the workspace root
-> complete URL and static file path shown
-> user selects in conversation
-> version-2 site-design-spec.json written and validated
-> user explicitly approves in conversation
-> implementation plan written
```

State that automatic-open failure is non-blocking, server failure uses the
static file, remote loopback requires an existing authorized port forward, and
browser activity never advances state.

Update the brainstorming contract and artifact layout with the same ownership
and lifecycle boundaries. Update README usage examples for Codex, Claude Code,
Cursor, Copilot CLI, and generic local agents without claiming support where
Node, shell, filesystem, or browser routing is absent.

- [ ] **Step 4: Run focused and full verification**

Run:

```powershell
python -m unittest tests.test_workflow_behavior_contract tests.test_visual_companion -v
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode skeleton
python skills/build-resume-portfolio-site/scripts/validate_skill_resources.py --mode runtime --stage discovery
```

Expected: all tests pass and both resource validations succeed.

- [ ] **Step 5: Commit**

```powershell
git add -- skills/build-resume-portfolio-site/SKILL.md skills/build-resume-portfolio-site/references/site-brainstorming-contract.md skills/build-resume-portfolio-site/references/artifact-layout.md README.md tests/test_workflow_behavior_contract.py
git commit -m "docs: integrate visual preview approval gate"
```

### Task 6: End-to-End Smoke Test and Installed-Copy Verification

**Files:**

- Modify only if a defect is found: files introduced or changed in Tasks 1–5.

**Interfaces:**

- Consumes: packaged plugin source.
- Produces: verified local session, static fallback, clean stop, and installable Skill resources.

- [ ] **Step 1: Run all repository tests**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run every Python Skill script test**

Run:

```powershell
python -m unittest discover -s skills/build-resume-portfolio-site/scripts -p "test_*.py" -v
```

Expected: all tests pass.

- [ ] **Step 3: Perform a real local session smoke test**

Create a temporary gallery outside the Skill directory, launch:

```powershell
$visualLaunch = node skills/build-resume-portfolio-site/scripts/visual_companion/launch.cjs --workspace-root "$env:TEMP\resume-visual-smoke" --gallery skills/build-resume-portfolio-site/assets/visual-companion/gallery-shell.html | ConvertFrom-Json
```

Use the returned authenticated URL with an HTTP client, confirm status `200`,
then stop with:

```powershell
node skills/build-resume-portfolio-site/scripts/visual_companion/stop.cjs --workspace-root "$env:TEMP\resume-visual-smoke" --server-info $visualLaunch.server_info
```

Expected: startup, authenticated request, and exact-session stop succeed;
`gallery.html` remains; no `.resume-site-work/site` directory exists.

- [ ] **Step 4: Validate Skill structure**

Run:

```powershell
python C:/Users/86135/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/build-resume-portfolio-site
git diff --check HEAD~5..HEAD
git status --short
```

Expected: Skill validation passes, no whitespace errors, and the source
repository is clean.

- [ ] **Step 5: Synchronize the verified Skill**

Copy the three verified Skill directories from this plugin source to the
user's Codex Skill directory only after source verification succeeds. Preserve
unrelated installed Skills and compare hashes for the modified website Skill.
Because that destination is outside the workspace, request scoped approval
before writing it.

- [ ] **Step 6: Verify the installed copy**

Run the installed Skill's resource validator and Node syntax checks from its
own path. Expected: the installed copy passes the same discovery validation
and exposes the same file hashes as the source.
