---
resource_id: repair-local-issues
resource_version: 1
resource_status: ready
output_contract: react-vite-project-update
---

# Repair validated local visual findings

Read the validated `reports/visual-audit.json`, approved
`reports/design-contract.json`, current source, capture evidence, and last valid
preview. Repair only findings with `blocking` or `repairable` severity.

For each repair:

1. Confirm its `rule_id`, `contract_path`, `evidence_refs`, `permitted_files`,
   proposed local change, and intended result.
2. Modify only the listed `permitted_files` and the smallest affected DOM/CSS
   region capable of producing the intended result.
3. Preserve approved content, facts, structure, primary motion, and every
   unrelated design-contract path.
4. Do not select a new style, replace the primary motion system, rewrite the
   complete page, or broaden scope to advisory findings.
5. Validate and build before promotion. Re-capture desktop, tablet, mobile, and
   every affected interaction, coarse-pointer, reduced-motion, loading, error,
   or Poster state.
6. Re-run the visual audit validator against the same approved design contract.

Count only completed repairs toward the maximum of two completed visual repair
rounds. Infrastructure retries do not consume a round. Validation, build,
capture, or audit failure leaves the last valid preview active.

After round two, stop with `visual_blocked` and the remaining screenshot-backed
blocking findings. If blocking and repairable findings are resolved, preserve
advisory findings for presentation and continue to integrated confirmation
without another user approval gate.
