# Delivery Workflow

Read this guide only when entering this phase. All paths are relative to the
Skill root unless explicitly workspace-relative. Resolve `SKILL_ROOT` and the
Python executable as described in `SKILL.md`.

Before starting, read:

- [screenshot-review-rules.md](screenshot-review-rules.md)
- [react-vite-output-contract.md](react-vite-output-contract.md)

## Final acceptance

Before acceptance, follow [resume-export-contract.md](resume-export-contract.md)
to export the selected approved content as printable HTML and a real PDF.
Check extracted text order, page rendering and links. Default to a private
delivery; include a website download only for explicitly approved public blocks.
Copy only that public PDF into `site/public/`, then rebuild and check the download
in the built preview. Promote this successful build to the preview and create a
new integrated snapshot containing the PDF and download link before final
acceptance; make that snapshot the accepted rollback baseline. Keep evidence,
role comparisons and export reports local.
Explain if a dependency or font limitation prevents PDF completion; an HTML file
alone does not satisfy PDF delivery. Give the user source, build, PDF and HTML
locations plus checks actually completed.

For version libraries, show the active version label and how to select another
version using `manage_resume_versions.py`. Re-export after any approved copy
change; stale plans fail their content hash check.

Offer exactly three outcomes:

1. `当前效果满意，完成`
2. `加强动效`
3. `提出修改`

On `当前效果满意，完成`, set the integrated snapshot as
`last_confirmed_artifact` and set `stage=complete`.

On `加强动效`, restore the last valid integrated snapshot and change only the
motion layer. Preserve content, structure, typography, color, and media
treatment. Enter `motion_enhancing`, read
`references/motion-production-contract.md`, and re-plan controller ownership,
mobile/coarse-pointer behavior, cleanup, fallback, and reduced motion. Apply all
compatible planned effects without a numeric effect cap, validate/build/capture,
snapshot an integrated retry, then return to `integrated_waiting_confirmation`.

On `提出修改`, route bounded feedback to local repair. If feedback reverses a
core decision, invalidate its affected downstream decisions and approvals.
In quick mode, show and reapprove the changed design/execution bundle; in deep
mode, return to the affected category, reconfirm requirements and TODO plan.
Regenerate validated planning artifacts before a new integrated candidate.

