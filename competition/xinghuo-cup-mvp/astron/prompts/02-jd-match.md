# 02 Match Target JD

## Inputs

- `target_role`
- `jd_text`
- `source_facts`
- `confirmed_facts`
- `evidence`

## Instruction

Decompose the JD into `hard_requirement`, `core_capability`, and
`bonus_signal`. Record the exact phrase and normalized concept. Match only to a
`FACT-*` item backed by an `EVID-*` item or explicit `user_confirmed` status.

Use only `strong_match`, `partial_match`, `transferable`, or `unmatched`.
`unmatched` must remain visible. Never add a JD keyword, skill, seniority,
metric, or responsibility merely to improve apparent fit. Suggest one factual
clarification only when the resume plausibly hints that evidence is missing.

## Output

Return JSON only:

```json
{
  "target_role":"",
  "requirements":[{"jd_phrase":"","kind":"core_capability","priority":1}],
  "jd_match_matrix":[{"jd_phrase":"","fact_ids":["FACT-001"],"evidence_ids":["EVID-001"],"status":"partial_match","resume_location":"projects"}],
  "unmatched_requirements":[],
  "recommended_emphasis":[]
}
```
