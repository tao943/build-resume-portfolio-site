# Site Brainstorming Contract

Use the full workflow for a new site or any change to audience, structure,
visual thesis, layout family, interaction architecture, or implementation
strategy.

1. Inspect the approved content package, authorized media, references,
   existing site state, and confirmed artifacts.
2. Ask one decision-bearing question at a time.
3. Compare two or three materially different layout or experience families.
4. Recommend one with explicit fit, risk, and responsive trade-offs.
5. Define the visual protagonist, composition commitment, type/color
   character, representative interaction, fixed constraints, open ceiling,
   and avoid rules.
6. Read `visual-style-preview-contract.md` and create one display-only
   `gallery.html` that shows all two or three alternatives with approved
   content. Keep it outside the React source project.
7. Start the local companion when possible. Always provide the complete
   authenticated URL and the standalone HTML fallback.
8. Receive the candidate selection and explicit approval in the conversation.
   Browser activity never counts as approval and never advances state.
9. Write schema-version-2
   `.resume-site-work/reports/site-design-spec.json`.
10. Validate it before creating the implementation plan.

Do not edit React source before the approved site design specification exists.
Do not infer approval from a browser visit, screenshot, automatic launch, or
silence.

Fast change is allowed only with a validated workflow route, a confirmed
artifact, exact affected files, verification, and rollback baseline. If scope
expands, return to the full workflow.
