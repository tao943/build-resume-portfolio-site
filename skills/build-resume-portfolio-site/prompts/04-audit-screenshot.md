---
resource_id: audit-screenshot
resource_version: 2
resource_status: ready
output_contract: visual-audit-json
---

# Audit screenshots against the approved design contract

Audit the successful built preview without redesigning it. Read
`references/screenshot-review-rules.md`, validated
`reports/design-contract.json`, `capture-report.json`, and every required
desktop, tablet, mobile, interaction, coarse-pointer, reduced-motion, loading,
error, and Poster capture.

Write schema-version-1 `reports/visual-audit.json` with:

- `captures` containing stable evidence IDs and local capture paths;
- `deterministic_checks` linked to a known `rule_id`, `evidence_refs`, and
  `contract_path`;
- separate `dimension_reviews.identity_fit` and
  `dimension_reviews.aesthetic_quality` verdicts, strengths, evidence, contract
  paths, and `pass`, `repairable`, or `blocking` status;
- `findings` for every observable defect;
- `interaction_states_checked`; and
- an `overall_status` at least as severe as every dimension and finding.

Identity fit and aesthetic quality are independent. Neither can compensate for
failure of the other. A numerical score is diagnostic only when its rubric and
evidence are explicit; status and observable findings control repair.

## Finding contract

Every finding contains:

```json
{
  "id": "finding-001",
  "rule_id": "aesthetic.signature-visible",
  "dimension": "aesthetic_quality",
  "severity": "repairable",
  "viewport_or_state": "mobile-initial",
  "region": "projects",
  "evidence_refs": ["mobile-initial"],
  "contract_path": "signature.structural_device",
  "permitted_files": [
    "src/components/ProjectsSection.jsx",
    "src/styles/projects.css"
  ],
  "proposed_local_change": "Restore project-number prominence on mobile.",
  "intended_result": "The signature index remains immediately recognizable."
}
```

Use only source-relative permitted files inside `.resume-site-work/site`. Do not
invent a finding, rule, contract path, capture, interaction, or factual defect.

## Validation and repair decision

Before any repair, run:

```powershell
python "$SKILL_ROOT\scripts\validate_visual_audit.py" `
  ".resume-site-work\reports\visual-audit.json" `
  --design-contract ".resume-site-work\reports\design-contract.json"
```

Continue only on exit `0`. For `blocking` or `repairable` findings, enter
`prompts/05-repair-local-issues.md`. Advisory findings do not extend the repair
loop. Preserve the last valid preview on audit or validation failure. Keep the
existing maximum of two completed repair rounds and add no user confirmation.
