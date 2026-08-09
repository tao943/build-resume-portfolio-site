# 03 Create Content Strategies

## Inputs

- `confirmed_facts`
- `jd_match_matrix`
- `target_role`

## Instruction

Create two or three materially different career narratives. Every thesis must
be supported by linked `FACT-*` and `EVID-*` items. Do not disguise an
`unmatched` requirement as a strength. Recommend one strategy using relevance,
evidence density, differentiation, and risk; explain real trade-offs.

This step proposes positioning only. It does not approve wording and must not
write `approved_copy`.

## Output

Return JSON only:

```json
{
  "strategies":[{"id":"strategy-1","thesis":"","fact_ids":[],"evidence_ids":[],"fit":"","risks":[],"tradeoffs":[]}],
  "recommended_strategy_id":"strategy-1",
  "recommendation_reason":""
}
```
