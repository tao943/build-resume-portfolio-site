# 05 Build Content Map

## Inputs

- `approved_copy`
- `confirmed_facts`
- `jd_match_matrix`
- `public_name`
- `contact_visibility`

## Instruction

Arrange only `approved_copy` into a one-page attention sequence. Prioritize a
role-specific proposition, strongest evidence, selected projects, experience,
skills, and authorized contact details. You may omit or shorten a block only by
selecting an already approved shorter variant; do not silently rewrite it.

Never expose contact data unless its exact value is listed in
`contact_visibility.allowed_values`. Never promote inference or an
`unmatched` JD item.

## Output

Return JSON only:

```json
{
  "content_map":{"order":["hero","evidence","projects","experience"],"regions":[{"id":"hero","copy_keys":["hero"],"priority":1}],"public_contacts":[]},
  "private_omissions":[],
  "fact_ids_used":[]
}
```
