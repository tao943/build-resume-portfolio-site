# APIHz Optional Media Contract

APIHz is an optional source for user-requested meme images and animated GIFs. It is not a required portfolio stage and must not replace user media, factual project screenshots, profile photography, generated thematic artwork, or reference-derived styling.

## Credentials and endpoint

Read `APIHZ_ID` and `APIHZ_KEY` from the process environment. Never write either value to reports, logs, React source, preview files, or Git. Operators may add exact trusted CDN hosts through comma-separated `APIHZ_ASSET_HOSTS`.

Use `https://cn.apihz.cn/api/img/apihzbqb.php`. Keyword searches send `type=2`, `words`, `page`, and `limit`. Random searches send `type=1` only after an explicit user request. Keywords are at most ten characters, the default limit is ten, and the hard limit is twenty.

## Manifest

Every search writes a schema-version-1 manifest below `.resume-site-work/media-search/<search-id>/manifest.json`. Candidate records follow `references/apihz-media-schema.json`. Verified GIF bytes use `asset_type: "gif"`; JPG, PNG, and WebP use `asset_type: "image"`. Width and height may be `null` when no optional image decoder is available.

Every candidate carries this publication warning:

```text
source collected from the public web; publication rights not verified
```

## User gate

Show the local preview before importing anything. Only candidate IDs explicitly selected by the user may be copied into `.resume-site-work/site/public/assets/external/`. React code uses project-local `/assets/external/...` paths and never hotlinks an APIHz URL.

## Failure isolation

Stable categories are `credentials_missing`, `credentials_invalid`, `query_invalid`, `api_rejected`, `rate_limited`, `network_failed`, `invalid_response`, `unsafe_url`, `requires_host_configuration`, `unsupported_media`, `file_too_large`, `download_failed`, and `selection_invalid`. APIHz failure leaves the normal prototype, style, repair, motion, and build workflow available.
