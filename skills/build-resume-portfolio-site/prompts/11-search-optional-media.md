---
resource_id: search-optional-media
resource_version: 1
resource_status: ready
output_contract: local-apihz-candidate-preview-and-selected-project-assets
---

# Search optional APIHz media

Use this resource only after an explicit user request for a meme, reaction image, humorous image, or animated GIF. APIHz is optional media retrieval, not a visual-style stage and not a remedy for missing factual assets.

Obtain a keyword of at most ten characters or an explicit random-search request, then run the APIHz search command. Show the resulting local `preview.html` and the warning `publication rights not verified`. Preserve animated GIF playback in the preview.

Stop and wait for explicit candidate IDs. Do not infer selection from the search keyword, candidate order, visual similarity, or silence. After selection, run the selected-only importer and use only project-local `/assets/external/` paths in React. Never hotlink APIHz URLs.

Place imported media as secondary expressive material compatible with the confirmed content and design direction. A meme does not dictate the site's visual language. Never substitute it for a profile photograph, client work, project screenshot, credential, brand asset, factual diagram, or user-supplied media.

If credentials, the provider, the network, or all candidates fail validation, leave the current site and build state unchanged. Offer user-supplied media or original decorative image generation instead.
