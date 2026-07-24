# Workflow Contract

## State machine

Persist state after every transition. Never infer approval from silence or from a previous stage.

```text
prototype_generating -> prototype_waiting_confirmation
prototype_waiting_confirmation --confirm--> media_direction_generating
prototype_waiting_confirmation --reject--> prototype_generating
media_direction_generating -> media_direction_waiting_confirmation
media_direction_waiting_confirmation --confirm--> screenshot_auditing
media_direction_waiting_confirmation --reject--> media_direction_generating
screenshot_auditing --clean--> motion_generating
screenshot_auditing --repairable and rounds<2--> screenshot_repairing -> screenshot_auditing
screenshot_auditing --blocking and rounds=2--> visual_blocked
motion_generating -> motion_waiting_confirmation
motion_waiting_confirmation --confirm current motion--> complete
motion_waiting_confirmation --enhance--> motion_enhancement_selecting
motion_waiting_confirmation --reject--> motion_generating
```

The optional motion continuation is an optional branch selected from the existing motion confirmation. Do not enter it without explicit user selection, and do not improvise MotionSite material when its approved local catalog is unavailable.

The optional second layer and later video upgrade use these exact transitions:

```text
motion_enhancement_selecting -> motion_media_slot_planning
motion_media_slot_planning --video-capable--> motion_poster_generating
motion_media_slot_planning --no-media-needed--> motion_enhancement_generating
motion_poster_generating -> motion_enhancement_generating
motion_enhancement_generating -> motion_waiting_confirmation
complete --video supplied and upgrade available--> video_upgrade_validating
video_upgrade_validating --validate/build/promote--> complete
video_upgrade_validating --failure--> complete with confirmed Poster restored
```

## Stage transaction

Every generating or repair transition is one transaction:

1. Restore the correct baseline snapshot when retrying.
2. Edit the single React + Vite project at `.resume-site-work/site/`.
3. Run `validate_vite_project.py` with the current stage.
4. Run `npm run build` from `site/`.
5. Replace `.resume-site-work/preview/dist/` with the successful `site/dist/` output.
6. Save an immutable source snapshot for the new candidate.
7. Capture and show `preview/dist/index.html`, then update state.

If validation or build fails, keep the previous valid preview and confirmed snapshot active.

## Confirmation gates

1. Show the built prototype preview and wait for explicit prototype confirmation.
2. Show the built media-direction preview and wait for explicit media-direction confirmation.
3. Show the built source-agnostic production-hardened motion preview and its reduced-motion behavior. Ask the user to choose either `当前动效足够，完成` or `继续加强动效`; enhancement returns to this same motion confirmation.

Run screenshot audit and local repair without routine confirmation. Stop after two visual repair rounds if blocking defects remain.

## Rollback

- Retry a rejected prototype from the original normalized inputs and an empty/new `site/` project.
- Retry rejected media direction by restoring `versions/v1-prototype` to `site/`, recording feedback and the selected ID in `attempted_media_direction_ids`, then implementing one new winner.
- Retry screenshot repair by restoring the latest valid media-direction/refined candidate as appropriate.
- Retry rejected motion by restoring `versions/v3-refined`, never from a partially animated project.
- Replace an automatically generated or user-supplied Poster through ordinary feedback while retaining `versions/v4-motion` as the motion baseline.
- Retry video upgrade from `versions/v5-motion-enhanced-poster` and edit only the media layer; a failed upgrade atomically keeps or restores the confirmed Poster preview.
- Preserve every confirmed source snapshot and never overwrite version directories in place.

## Failure states

- Use `resource_blocked` when a required prompt, manifest, image, package dependency, browser dependency, shadcn MCP connection, or React Bits registry item is unavailable.
- Use `artifact_invalid` when React/Vite source validation fails.
- Use `build_failed` when `npm run build` fails; do not publish or capture stale `dist/` output.
- Retry screenshot infrastructure once without incrementing `visual_repair_round`.
- Use `visual_blocked` when two completed visual rounds leave blocking defects.

## State compatibility

`build-state.json` has schema version `3`. Systems reject unsupported old state schemas rather than guessing a migration. Set `confirmations.media_direction` only after explicit user confirmation; its confirmation keys are `prototype`, `media_direction`, and `motion`. Do not create a separate confirmation for a StyleBrief.

## Design-intelligence and media-direction transaction

Before `prototype_generating` edits React source, create `reports/design-intelligence.json` from `content-map.json`. Persist `selected_direction_id` and `attempted_direction_ids` in `build-state.json`. A rejected prototype selects an unused candidate before a new Catalog query.

During `media_direction_generating`, prepare a visual StyleBrief internally when references exist. Reference evidence has priority over Catalog aesthetics. When no reference manifest exists, continue with the Catalog-only input path; absence is not a malformed resource. A present malformed manifest remains `resource_blocked`.

Restore `versions/v1-prototype` before each media-direction attempt. Inspect the UI and authorized media, always write the trusted `reports/media-inventory.json` (or `{"schema_version": 1, "assets": []}`), then write `reports/media-art-direction.json`, select one ID not present in `attempted_media_direction_ids`, implement that winner in the same React + Vite project, and validate/build it with `--media-inventory` before promotion. Snapshot only a successful candidate to `versions/v2-media-direction`; a failed attempt never replaces the last valid preview.
## optional APIHz media transaction

APIHz media search is an explicit, optional side transaction:

```text
explicit media request -> search -> local preview -> wait for candidate IDs -> selected-only import -> optional React placement
```

It does not change the current portfolio stage, confirmation flags, `last_confirmed_artifact`, active preview, or snapshot baseline. Search candidates remain below `media-search/`; only selected verified files are copied into the React project. Provider errors record no state transition, and the normal workflow remains available.
