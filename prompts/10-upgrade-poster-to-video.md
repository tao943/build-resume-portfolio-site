---
resource_id: upgrade-poster-to-video
resource_version: 1
resource_status: ready
output_contract: react-vite-media-only-update-and-video-validation-json
---

# Upgrade a confirmed Poster to user-supplied video

Start from the confirmed `versions/v5-motion-enhanced-poster` snapshot. Validate the supplied local MP4/WebM before editing. Replace only the media source/component; do not re-run style selection, recipe selection, layout generation, or copy generation.

Keep the confirmed Poster permanently visible as loading, error, mobile-budget, and `prefers-reduced-motion` fallback. Video must be local, muted, looping, inline, metadata-preloaded, and pass the size/duration/container checks. Never connect playback time, mask, opacity, or visibility to scroll or pointer coordinates.

Write `reports/video-validation.json`, validate the `video-upgrade` stage, build and capture responsive screenshots, then wait for confirmation. On rejection restore the confirmed Poster snapshot. On confirmation save `versions/v6-video-upgrade`.
