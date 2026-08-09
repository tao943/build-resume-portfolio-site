# 06 Create Creative Directions

## Inputs

- `approved_copy`
- `content_map`
- `target_role`
- `authorized_media_summary`

## Instruction

Create two or three materially different, content-derived creative directions.
Do not choose from a fixed style catalog and do not output a component tree.
Each direction defines one visual protagonist, one profession-specific visual
metaphor, a composition commitment, type/color character, one representative
interaction, mobile fallback, fixed rules, open exploration space, and avoid
rules.

Reject the generic gradient hero + three skill cards + timeline + contact CTA
stack. Projects must not collapse into identical cards. The page must remain
recognizable after removing the name and without final imagery or complex
motion.

## Output

Return JSON only:

```json
{
  "directions":[{"id":"direction-1","creative_thesis":"","visual_protagonist":"","visual_metaphor":"","composition_commitment":"","type_color_character":"","representative_interaction":"","responsive_fallback":"","fixed":[],"open":[],"avoid":[],"fit":"","risks":[]}],
  "recommended_direction_id":"direction-1",
  "recommendation_reason":""
}
```

Only an explicit conversational selection may become `creative_direction`.
