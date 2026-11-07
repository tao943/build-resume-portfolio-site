# Delivery Workflow

Read this guide only when entering this phase. All paths are relative to the
Skill root unless explicitly workspace-relative. Resolve `SKILL_ROOT` and the
Python executable as described in `SKILL.md`.

Before starting, read:

- [screenshot-review-rules.md](screenshot-review-rules.md)
- [react-vite-output-contract.md](react-vite-output-contract.md)

## Final acceptance

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
core decision, return to that decision category, invalidate its downstream
decisions and approvals, reconfirm requirements, regenerate both plans, obtain
new TODO plan approval, and generate a new integrated candidate.

