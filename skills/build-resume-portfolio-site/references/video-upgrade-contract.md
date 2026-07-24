# Video Upgrade Contract

Video upgrade is media-only and always starts from the confirmed Poster snapshot. Accept local MP4 or WebM, 4–12 seconds, at most 50 MiB uploaded; target at most 15 MiB desktop and 8 MiB mobile. The embed is `muted`, `loop`, `playsInline`, and `preload="metadata"`.

The confirmed Poster remains the loading/error/reduced-motion fallback. If validation tools are unavailable, return `resource_blocked` and leave the Poster version intact. If the user rejects the result, restore the Poster snapshot without regenerating the page.
