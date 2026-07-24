from __future__ import annotations

import argparse
import hashlib
import html
import ipaddress
import json
import os
import socket
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen


APIHZ_ENDPOINT = "https://cn.apihz.cn/api/img/apihzbqb.php"
RIGHTS_NOTE = "source collected from the public web; publication rights not verified"
CHUNK_SIZE = 64 * 1024
MAX_API_RESPONSE_BYTES = 1024 * 1024
Resolver = Callable[[str], tuple[str, ...]]
OpenRequest = Callable[[Request, float], object]


class APIHzError(RuntimeError):
    """Stable, credential-safe error raised by the APIHz media adapter."""

    def __init__(self, category: str, message: str) -> None:
        self.category = category
        super().__init__(f"{category}: {message}")


@dataclass(frozen=True)
class APIHzConfig:
    developer_id: str
    developer_key: str
    endpoint: str = APIHZ_ENDPOINT
    timeout_seconds: float = 15.0
    max_bytes: int = 12 * 1024 * 1024
    retries: int = 2
    extra_asset_hosts: tuple[str, ...] = ()

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "APIHzConfig":
        developer_id = env.get("APIHZ_ID", "").strip()
        developer_key = env.get("APIHZ_KEY", "").strip()
        if not developer_id or not developer_key:
            raise APIHzError(
                "credentials_missing",
                "configure APIHZ_ID and APIHZ_KEY before searching APIHz media",
            )
        if any(ord(char) < 32 for char in developer_id + developer_key):
            raise APIHzError("credentials_invalid", "credentials contain control characters")

        hosts = tuple(
            sorted(
                {
                    host.strip().lower().rstrip(".")
                    for host in env.get("APIHZ_ASSET_HOSTS", "").split(",")
                    if host.strip()
                }
            )
        )
        return cls(
            developer_id=developer_id,
            developer_key=developer_key,
            extra_asset_hosts=hosts,
        )


@dataclass(frozen=True)
class SearchQuery:
    words: str | None
    page: int
    limit: int
    random: bool

    @classmethod
    def create(
        cls,
        *,
        words: str | None,
        page: int = 1,
        limit: int = 10,
        random: bool = False,
    ) -> "SearchQuery":
        normalized = words.strip() if words else None
        if page < 1 or not 1 <= limit <= 20:
            raise APIHzError(
                "query_invalid",
                "page must be positive and limit must be between 1 and 20",
            )
        if not random and (not normalized or len(normalized) > 10):
            raise APIHzError(
                "query_invalid",
                "keyword search requires a non-empty keyword of at most 10 characters",
            )
        return cls(
            words=None if random else normalized,
            page=page,
            limit=limit,
            random=random,
        )


def build_api_url(config: APIHzConfig, query: SearchQuery) -> str:
    params = {
        "id": config.developer_id,
        "key": config.developer_key,
        "type": "1" if query.random else "2",
        "limit": str(query.limit),
    }
    if not query.random:
        params.update(words=query.words or "", page=str(query.page))
    return f"{config.endpoint}?{urlencode(params)}"


def parse_api_response(payload: bytes) -> tuple[str, ...]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise APIHzError("invalid_response", "APIHz returned malformed JSON") from exc

    if not isinstance(value, dict):
        raise APIHzError("invalid_response", "APIHz response must be a JSON object")

    code = value.get("code")
    if code != 200:
        message = value.get("msg")
        safe_message = message if isinstance(message, str) and message.strip() else "request rejected"
        if any(marker in safe_message for marker in ("频繁", "限流", "稍后", "次数")):
            raise APIHzError("rate_limited", safe_message)
        raise APIHzError("api_rejected", safe_message)

    raw_urls = value.get("res")
    if not isinstance(raw_urls, list):
        raise APIHzError("invalid_response", "APIHz response is missing the result list")

    urls = tuple(item.strip() for item in raw_urls if isinstance(item, str) and item.strip())
    if not urls or len(urls) != len(raw_urls):
        raise APIHzError("invalid_response", "APIHz result list contains no usable URLs")
    return urls


def _read_limited(response: object, limit: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(min(CHUNK_SIZE, limit + 1 - total))
        if not chunk:
            return b"".join(chunks)
        total += len(chunk)
        if total > limit:
            raise APIHzError("invalid_response", "APIHz response exceeded the size limit")
        chunks.append(chunk)


def _is_transient_http(status: int) -> bool:
    return status in (408, 429) or 500 <= status <= 599


def open_url(request: Request, timeout: float) -> object:
    return urlopen(request, timeout=timeout)


def fetch_api_urls(    config: APIHzConfig,
    query: SearchQuery,
    *,
    open_request: OpenRequest = open_url,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[str, ...]:
    request = Request(
        build_api_url(config, query),
        headers={"Accept": "application/json", "User-Agent": "ResumeSite-Agent/1.0"},
    )
    for attempt in range(config.retries + 1):
        try:
            with open_request(request, config.timeout_seconds) as response:
                status = int(getattr(response, "status", 200))
                if status == 429:
                    raise APIHzError("rate_limited", "APIHz rate limit reached")
                if status >= 400:
                    raise APIHzError("network_failed", f"APIHz returned HTTP {status}")
                return parse_api_response(_read_limited(response, MAX_API_RESPONSE_BYTES))
        except APIHzError:
            raise
        except HTTPError as exc:
            if exc.code == 429:
                raise APIHzError("rate_limited", "APIHz rate limit reached") from exc
            if not _is_transient_http(exc.code) or attempt >= config.retries:
                raise APIHzError("network_failed", "APIHz request failed") from exc
        except (TimeoutError, URLError, OSError) as exc:
            if attempt >= config.retries:
                raise APIHzError("network_failed", "APIHz request failed") from exc
        sleep(0.15 * (attempt + 1))
    raise APIHzError("network_failed", "APIHz request failed")


def resolve_host(host: str) -> tuple[str, ...]:
    try:
        records = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise APIHzError("unsafe_url", "asset host could not be resolved") from exc
    return tuple(sorted({record[4][0] for record in records}))


def _host_is_trusted(host: str, config: APIHzConfig) -> bool:
    return (
        host == "res.apihz.cn"
        or host.endswith(".apihz.cn")
        or host in config.extra_asset_hosts
    )


def validate_asset_url(
    url: str,
    config: APIHzConfig,
    resolver: Resolver = resolve_host,
) -> str:
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise APIHzError("unsafe_url", "asset URL is malformed") from exc
    host = (parsed.hostname or "").lower().rstrip(".")
    if (
        parsed.scheme.lower() != "https"
        or not host
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or port not in (None, 443)
    ):
        raise APIHzError("unsafe_url", "asset URL must be credential-free HTTPS on port 443")
    if not _host_is_trusted(host, config):
        raise APIHzError(
            "requires_host_configuration",
            "asset host must be added to APIHZ_ASSET_HOSTS before download",
        )
    addresses = resolver(host)
    if not addresses:
        raise APIHzError("unsafe_url", "asset host resolved to no addresses")
    try:
        parsed_addresses = tuple(ipaddress.ip_address(address) for address in addresses)
    except ValueError as exc:
        raise APIHzError("unsafe_url", "asset host returned an invalid address") from exc
    if any(not address.is_global for address in parsed_addresses):
        raise APIHzError("unsafe_url", "asset host resolved to a non-public address")
    return url


class ValidatedRedirectHandler(HTTPRedirectHandler):
    max_redirections = 5

    def __init__(self, config: APIHzConfig, resolver: Resolver) -> None:
        super().__init__()
        self._config = config
        self._resolver = resolver

    def redirect_request(
        self,
        req: Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> Request | None:
        validate_asset_url(newurl, self._config, self._resolver)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def detect_media_format(header: bytes) -> tuple[str, str]:
    if header.startswith(b"\xff\xd8\xff"):
        return "jpg", "image"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png", "image"
    if header.startswith((b"GIF87a", b"GIF89a")):
        return "gif", "gif"
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "webp", "image"
    raise APIHzError("unsupported_media", "downloaded bytes are not JPG, PNG, WebP, or GIF")


def _default_asset_opener(config: APIHzConfig, resolver: Resolver) -> OpenRequest:
    opener = build_opener(ValidatedRedirectHandler(config, resolver))
    return lambda request, timeout: opener.open(request, timeout=timeout)


def _download_one(
    source_url: str,
    candidates_dir: Path,
    config: APIHzConfig,
    resolver: Resolver,
    open_request: OpenRequest,
) -> dict[str, object]:
    validate_asset_url(source_url, config, resolver)
    request = Request(
        source_url,
        headers={"Accept": "image/avif,image/webp,image/png,image/jpeg,image/gif", "User-Agent": "ResumeSite-Agent/1.0"},
    )
    part_path: Path | None = None
    try:
        with open_request(request, config.timeout_seconds) as response:
            final_url = str(response.geturl())
            validate_asset_url(final_url, config, resolver)
            content_length = response.headers.get("Content-Length") if hasattr(response, "headers") else None
            if content_length:
                try:
                    if int(content_length) > config.max_bytes:
                        raise APIHzError("file_too_large", "asset exceeds the twelve-megabyte limit")
                except ValueError:
                    pass

            candidates_dir.mkdir(parents=True, exist_ok=True)
            descriptor, raw_part = tempfile.mkstemp(prefix=".download-", suffix=".part", dir=candidates_dir)
            os.close(descriptor)
            part_path = Path(raw_part)
            digest = hashlib.sha256()
            header = bytearray()
            total = 0
            with part_path.open("wb") as stream:
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > config.max_bytes:
                        raise APIHzError("file_too_large", "asset exceeds the twelve-megabyte limit")
                    if len(header) < 32:
                        header.extend(chunk[: 32 - len(header)])
                    digest.update(chunk)
                    stream.write(chunk)
            if total == 0:
                raise APIHzError("unsupported_media", "downloaded asset is empty")
            media_format, asset_type = detect_media_format(bytes(header))
            sha256 = digest.hexdigest()
            candidate_id = f"media-{sha256[:12]}"
            final_path = candidates_dir / f"{candidate_id}.{media_format}"
            if final_path.exists():
                part_path.unlink(missing_ok=True)
            else:
                part_path.replace(final_path)
            part_path = None
            return {
                "id": candidate_id,
                "provider": "apihz",
                "asset_type": asset_type,
                "format": media_format,
                "preview_path": f"candidates/{final_path.name}",
                "source_url": source_url,
                "width": None,
                "height": None,
                "byte_size": total,
                "sha256": sha256,
                "rights_note": RIGHTS_NOTE,
                "selected": False,
            }
    finally:
        if part_path is not None:
            part_path.unlink(missing_ok=True)


def download_candidates(
    urls: Sequence[str],
    search_root: Path,
    config: APIHzConfig,
    *,
    resolver: Resolver = resolve_host,
    open_request: OpenRequest | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[tuple[dict[str, object], ...], tuple[dict[str, str], ...]]:
    candidates_dir = search_root / "candidates"
    actual_open = open_request or _default_asset_opener(config, resolver)
    candidates: list[dict[str, object]] = []
    rejected: list[dict[str, str]] = []
    known_hashes: set[str] = set()
    for source_url in urls:
        for attempt in range(config.retries + 1):
            try:
                candidate = _download_one(source_url, candidates_dir, config, resolver, actual_open)
                sha256 = str(candidate["sha256"])
                if sha256 not in known_hashes:
                    known_hashes.add(sha256)
                    candidates.append(candidate)
                break
            except APIHzError as exc:
                rejected.append({"source_url": source_url, "category": exc.category})
                break
            except HTTPError as exc:
                if _is_transient_http(exc.code) and attempt < config.retries:
                    sleep(0.15 * (attempt + 1))
                    continue
                rejected.append({"source_url": source_url, "category": "download_failed"})
                break
            except (URLError, TimeoutError, OSError):
                if attempt < config.retries:
                    sleep(0.15 * (attempt + 1))
                    continue
                rejected.append({"source_url": source_url, "category": "download_failed"})
                break
    return tuple(candidates), tuple(rejected)


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def write_search_artifacts(
    search_root: Path,
    *,
    search_id: str,
    query: SearchQuery,
    candidates: Sequence[Mapping[str, object]],
    rejected: Sequence[Mapping[str, str]],
    created_at: str,
) -> tuple[Path, Path]:
    manifest = {
        "schema_version": 1,
        "search_id": search_id,
        "provider": "apihz",
        "query": {
            "mode": "random" if query.random else "keyword",
            "words": query.words,
            "page": query.page,
            "limit": query.limit,
        },
        "created_at": created_at,
        "candidates": list(candidates),
        "rejected": list(rejected),
        "rights_note": RIGHTS_NOTE,
    }
    manifest_path = search_root / "manifest.json"
    _atomic_write_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    cards: list[str] = []
    for candidate in candidates:
        preview_path = html.escape(str(candidate["preview_path"]), quote=True)
        candidate_id = html.escape(str(candidate["id"]))
        media_format = html.escape(str(candidate["format"]).upper())
        source_host = html.escape(urlsplit(str(candidate["source_url"])).hostname or "unknown")
        byte_size = int(candidate["byte_size"])
        cards.append(
            f'<article class="card"><img src="{preview_path}" alt="APIHz candidate {candidate_id}" loading="lazy">'
            f'<div class="meta"><strong>{candidate_id}</strong><span>{media_format} · {byte_size} bytes</span>'
            f'<span>{source_host}</span></div></article>'
        )
    body = "\n".join(cards) or '<p class="empty">No safe media candidates were downloaded.</p>'
    preview = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>APIHz media candidates</title><style>
:root{{font-family:Inter,system-ui,sans-serif;color:#17211d;background:#f4f2ec}}body{{margin:0;padding:32px}}main{{max-width:1200px;margin:auto}}.warning{{padding:16px;border:1px solid #c38325;background:#fff7df}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;margin-top:24px}}.card{{background:white;border:1px solid #d8d5cc;padding:12px}}img{{display:block;width:100%;height:260px;object-fit:contain;background:#eee}}.meta{{display:grid;gap:6px;margin-top:12px;font-size:13px}}.empty{{padding:32px;background:white}}
</style></head><body><main><h1>APIHz 图片与 GIF 候选</h1><p class="warning">{html.escape(RIGHTS_NOTE)}. 请在导入前确认内容适当性与发布权利。</p><section class="grid">{body}</section></main></body></html>
"""
    preview_path = search_root / "preview.html"
    _atomic_write_text(preview_path, preview)
    return manifest_path, preview_path


def search_media(
    workspace_root: Path,
    config: APIHzConfig,
    query: SearchQuery,
    *,
    resolver: Resolver = resolve_host,
    api_open_request: OpenRequest = open_url,
    asset_open_request: OpenRequest | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    fingerprint = hashlib.sha256(
        f"{created_at}|{query.random}|{query.words}|{query.page}|{query.limit}".encode("utf-8")
    ).hexdigest()[:12]
    search_id = f"search-{fingerprint}"
    search_root = workspace_root.resolve() / ".resume-site-work" / "media-search" / search_id
    urls = fetch_api_urls(config, query, open_request=api_open_request, sleep=sleep)
    candidates, rejected = download_candidates(
        urls,
        search_root,
        config,
        resolver=resolver,
        open_request=asset_open_request,
    )
    manifest_path, preview_path = write_search_artifacts(
        search_root,
        search_id=search_id,
        query=query,
        candidates=candidates,
        rejected=rejected,
        created_at=created_at,
    )
    return {
        "search_id": search_id,
        "manifest": str(manifest_path),
        "preview": str(preview_path),
        "accepted": len(candidates),
        "rejected": len(rejected),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search APIHz for optional image and GIF candidates")
    subparsers = parser.add_subparsers(dest="command", required=True)
    search = subparsers.add_parser("search")
    search.add_argument("--workspace-root", default=".")
    group = search.add_mutually_exclusive_group(required=True)
    group.add_argument("--words")
    group.add_argument("--random", action="store_true")
    search.add_argument("--page", type=int, default=1)
    search.add_argument("--limit", type=int, default=10)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        config = APIHzConfig.from_env(os.environ)
        query = SearchQuery.create(words=args.words, page=args.page, limit=args.limit, random=args.random)
        result = search_media(Path(args.workspace_root), config, query)
    except APIHzError as exc:
        print(json.dumps({"ok": False, "category": exc.category}, ensure_ascii=False))
        return 2 if exc.category in {"credentials_missing", "credentials_invalid", "query_invalid"} else 1
    print(json.dumps({"ok": True, **result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())