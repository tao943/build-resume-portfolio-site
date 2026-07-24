# Extract Resume Facts

Extract only facts present in the supplied source. Return structured records with `fact_id`, `value`, `source_ids`, `confidence`, and `confirmation_status`. Preserve dates and wording when uncertain. Put ambiguous content into `open_questions`; do not infer missing metrics or titles.
