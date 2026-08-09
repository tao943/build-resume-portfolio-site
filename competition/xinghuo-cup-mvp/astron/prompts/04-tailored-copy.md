# 04 Draft Tailored Copy

## Inputs

- `selected_strategy_id`
- `confirmed_facts`
- `evidence`
- `jd_match_matrix`
- `copy_feedback`

## Instruction

Draft concise Chinese resume and portfolio copy for the selected strategy.
Each block must cite supporting `FACT-*` and `EVID-*` IDs. Use exact JD terms
only when they accurately describe supported evidence. Keep `unmatched`
requirements out of the copy.

Use problem, responsibility, action, and result where evidence supports them.
If a metric cannot be verified, use a qualitative result or omit it. This is a
draft until the user explicitly approves it; set `approval_status` to
`pending_user_approval`, never `user_approved` yourself.

## Output

Return JSON only:

```json
{
  "draft_copy":{"hero":{"text":"","fact_ids":["FACT-001"],"evidence_ids":["EVID-001"],"approval_status":"pending_user_approval"}},
  "omitted_claims":[],
  "unmatched_requirements":[]
}
```

After explicit conversational approval, the workflow copies the unchanged
blocks into `approved_copy` and records `approval_status: user_approved`.
