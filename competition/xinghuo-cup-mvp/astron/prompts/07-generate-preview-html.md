# 07 Generate Preview HTML

## Inputs

- `approved_copy`
- `content_map`
- `creative_direction`
- `focused_revision_feedback`

## Instruction

Generate one complete, self-contained HTML document using only
`approved_copy`, `content_map`, and `creative_direction`.
Do not use a fixed portfolio template. Express the approved visual protagonist and composition
commitment in the rendered page rather than explaining them in prose.

No JavaScript. Do not use forms, iframes, remote fonts, trackers, external
stylesheets, images, video, audio, or unapproved media. CSS-only decoration is
allowed. Include a viewport meta tag, a mobile `@media` rule, semantic HTML,
visible keyboard focus, sufficient contrast, and a `prefers-reduced-motion`
fallback whenever transition or animation is used.

Do not introduce navigation labels or claims that are absent from
`approved_copy`, `content_map`, or `creative_direction`. Do not use the generic
gradient hero + three skill cards + timeline + contact CTA stack. At least one
project needs evidence-specific treatment and projects must not be identical
cards.

## Output

Return the HTML document only, starting with `<!doctype html>`. Do not wrap it
in Markdown fences. A focused revision may change presentation, but it must not
change approved wording or facts.
