# Artifact Layout

Create all generated material under `.resume-site-work/` in the active user workspace. Never write generated user content into the Skill directory.

```text
.resume-site-work/
|-- input/
|-- site/                         # only editable React + Vite source project
|-- versions/
|   |-- v1-prototype/             # confirmed-source candidates; excludes dist/node_modules
|   |-- v2-media-direction/
|   |-- v3-refined/
|   `-- v4-motion/
|-- preview/
|   `-- dist/                     # latest successful npm run build output
|-- screenshots/
|   |-- desktop.png
|   |-- tablet.png
|   `-- mobile.png
|-- reports/
|   |-- content-map.json
|   |-- reference-selection.json
|   |-- style-brief.json
|   |-- media-inventory.json       # trusted authorized-media facts and stable IDs
|   |-- media-art-direction.json
|   |-- visual-audit.json
|   |-- capture-report.json
|   `-- motion-plan.json
`-- build-state.json
```

`site/` is the sole source of truth. Do not maintain a separate HTML version. `preview/dist/` is disposable build output and must be replaced only after source validation and `npm run build` succeed.

`reports/media-inventory.json` has the workspace-owned shape `{"schema_version": 1, "assets": [...]}`. It is always created before media-direction report validation; use the explicit empty inventory `{"schema_version": 1, "assets": []}` when no media is authorized. Every asset records a stable `id`, `factual_meaning`, and a non-empty `immutable_facts` list; `role` and `source` are optional. The media-direction report validator uses this inventory as the only authorization and factual-preservation source.

Create immutable source snapshots with `scripts/snapshot_vite_project.py`. The tool excludes `node_modules`, `dist`, `.git`, nested `.resume-site-work`, and `__pycache__`. It refuses to overwrite an existing version directory.

Initialize `build-state.json` with this minimum shape:

```json
{
  "schema_version": 3,
  "skill_version": "1.1.0-react-vite",
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

Systems reject unsupported old state schemas rather than guessing a migration. Append user feedback with its stage and timestamp. Update `current_artifact` and `current_preview` only after validation and build succeed. Update `last_confirmed_artifact` only after explicit confirmation. Before retrying a rejected stage, restore the previous confirmed source snapshot into `site/`.

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
