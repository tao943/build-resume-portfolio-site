# Artifact Layout

Create all generated material under `.resume-site-work/` in the active user workspace. Never write generated user content into the Skill directory.

```text
.resume-site-work/
|-- input/
|   |-- source-manifest.json
|   |-- normalized-resume.json
|   `-- approved-copy.json
|-- site/                         # only editable React + Vite source project
|-- style-preview/                # display-only discovery evidence
|   |-- drafts/
|   |   `-- <category>/<draft-id>/gallery.html
|   `-- sessions/
|       `-- <session-id>/
|           |-- gallery.html
|           |-- assets/
|           `-- state/server-info.json
|-- versions/
|   |-- v1-integrated/            # first complete site; excludes dist/node_modules
|   `-- v1-integrated-motion-rN/  # optional motion-only enhancement retries
|-- preview/
|   `-- dist/                     # latest successful npm run build output
|-- screenshots/
|   |-- desktop.png
|   |-- tablet.png
|   `-- mobile.png
|-- reports/
|   |-- workflow-route.json
|   |-- site-design-spec.json     # explicit product/experience approval
|   |-- site-todo-plan.md         # readable plan shown and approved in conversation
|   |-- site-implementation-plan.json # files, dependencies, checks, rollback
|   |-- content-map.json
|   |-- content-provenance.json
|   |-- creative-direction.json    # fixed floor, open ceiling, and selected layout family
|   |-- multi-agent-implementation.json # only when multi-agent execution is authorized
|   |-- reference-selection.json
|   |-- style-brief.json
|   |-- media-inventory.json       # trusted authorized-media facts and stable IDs
|   |-- media-art-direction.json
|   |-- visual-audit.json
|   |-- capture-report.json
|   `-- motion-plan.json
|-- agent-reports/                # bounded task handoffs; no approval semantics
`-- build-state.json
```

`site/` is the sole source of truth. Do not maintain a separate HTML version. `preview/dist/` is disposable build output and must be replaced only after source validation and `npm run build` succeed.

`style-preview/` contains display-only discovery evidence. Its galleries are
not React source, production previews, confirmed snapshots, or publishable
site output. Browser activity has no approval semantics; only an explicit
conversation reply may be recorded in the schema-version-3 site design
specification. Category Galleries are independent rather than cumulative.
Stopping a local session preserves its gallery for review.

The three content files under `input/` plus
`reports/content-provenance.json` are owned by
`resume-content-intelligence`. The website builder validates and consumes
them; it does not rewrite them.

`reports/media-inventory.json` has the workspace-owned shape `{"schema_version": 1, "assets": [...]}`. It is always created before media-direction report validation; use the explicit empty inventory `{"schema_version": 1, "assets": []}` when no media is authorized. Every asset records a stable `id`, `factual_meaning`, and a non-empty `immutable_facts` list; `role` and `source` are optional. The media-direction report validator uses this inventory as the only authorization and factual-preservation source.

`reports/creative-direction.json` is created after design intelligence and
the approved site design specification, and before the first React source
edit. It carries the creative thesis,
`creative_freedom`, layout candidates, responsive and motion freedoms, and
review questions. It is not source code, a component tree, a new stage, or a
confirmation artifact.

`reports/site-design-spec.json` records all six category decisions and the
final requirements approval. `reports/site-todo-plan.md` is the readable plan
shown and explicitly approved in the conversation.
`reports/site-implementation-plan.json` records that approval plus the
plan-based recommendation, reasons, explicit conversational strategy selection,
selected strategy, exact files, task boundaries, interfaces, verification,
rollback, and the integrated snapshot target. All three gates complete before
React source edits. The
creative-direction report may translate the approved design spec into
implementation detail but may not contradict it.

`reports/multi-agent-implementation.json` exists only when the user explicitly
selects parallel multi-Agent implementation. It records the parallel-wave
strategy, dependencies,
waves, shared files, bounded write ownership, acceptance criteria, and
verification. Validate it before dispatch. Task handoffs go to
`agent-reports/<task-id>.md`; neither artifact creates a new confirmation gate
or changes the workflow stage.

Create immutable source snapshots with `scripts/snapshot_vite_project.py`. The tool excludes `node_modules`, `dist`, `.git`, nested `.resume-site-work`, and `__pycache__`. It refuses to overwrite an existing version directory.

Initialize `build-state.json` with this minimum shape:

```json
{
  "schema_version": 4,
  "skill_version": "1.2.0-react-vite",
  "workflow_mode": "full",
  "discovery": {
    "site_design_approved": false,
    "site_plan_validated": false
  },
  "stage": "prototype_generating",
  "editable_project": "site",
  "current_artifact": null,
  "current_preview": null,
  "last_confirmed_artifact": null,
  "confirmations": {"prototype": false, "media_direction": false, "motion": false},
  "resource_versions": {},
  "selected_reference_ids": [],
  "selected_media_direction_id": null,
  "attempted_media_direction_ids": [],
  "visual_repair_round": 0,
  "user_feedback": [],
  "unresolved_defects": [],
  "next_actions": ["generate_prototype"]
}
```

Schema version `4` is the only active shape. A schema-version-3 state may be
migrated with `scripts/migrate_build_state.py <source> <distinct-output>`;
the tool preserves prior confirmations and confirmed snapshots, derives no new
approval, and refuses in-place or overwrite migrations. Systems reject every
other unsupported schema rather than guessing. Append user feedback with its
stage and timestamp. Update `current_artifact` and `current_preview` only after
validation and build succeed. Update `last_confirmed_artifact` only after
explicit confirmation. Before retrying a rejected stage, restore the previous
confirmed source snapshot into `site/`.

## Optional external media

APIHz searches add only these workspace-owned artifacts:

```text
.resume-site-work/
|-- media-search/
|   `-- search-<id>/
|       |-- candidates/
|       |-- manifest.json
|       `-- preview.html
|-- reports/
|   `-- media-selection.json
`-- site/public/assets/external/
```

Candidate downloads remain outside the React project until the user selects IDs. Only verified selected files enter `site/public/assets/external/`; generated React code references them through `/assets/external/` paths.
