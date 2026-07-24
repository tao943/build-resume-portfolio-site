---
resource_id: plan-motion-media
resource_version: 1
resource_status: ready
output_contract: motion-media-slot-json-and-poster
---

# Resolve the media slot and create a Poster

Use the selected recipe's `placement_reference` only as composition guidance. The confirmed website's theme, content, hierarchy, responsive layout, and section order take priority. Resolve one media slot that fits the existing page and record both the original `placement_reference` and the final `resolved_placement`.

Create or select a decorative Poster before changing source code. Prefer a user-supplied image; otherwise generate a theme-consistent decorative image that supports rather than replaces portfolio content. The Poster must be local, at most 3 MiB, crop safely at mobile/desktop aspect ratios, and remain the permanent fallback.

Playback is passive only: muted loop, no scroll-linked reveal, no `currentTime` scrubbing, and no pointer-linked mask/playback. Return the media-slot JSON plus Poster path and show exactly four decisions: `使用 Poster 完成`, `使用 Poster 生成视频`, `更换 Poster`, `取消第二层动效`.
