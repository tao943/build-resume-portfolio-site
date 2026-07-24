from __future__ import annotations

import json
import tempfile
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from urllib.error import URLError
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from apihz_media import (  # noqa: E402
    APIHzConfig,
    APIHzError,
    SearchQuery,
    build_api_url,
    detect_media_format,
    download_candidates,
    fetch_api_urls,
    open_url,
    parse_api_response,
    validate_asset_url,
    write_search_artifacts,
)


class MemoryResponse:
    def __init__(self, body: bytes, *, url: str, status: int = 200, headers: dict[str, str] | None = None) -> None:
        self._body = body
        self._offset = 0
        self._url = url
        self.status = status
        self.headers = headers or {"Content-Length": str(len(body))}

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = len(self._body) - self._offset
        chunk = self._body[self._offset : self._offset + size]
        self._offset += len(chunk)
        return chunk

    def geturl(self) -> str:
        return self._url

    def __enter__(self) -> "MemoryResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None


class APIHzConfigurationTests(unittest.TestCase):
    def test_config_requires_environment_credentials(self) -> None:
        with self.assertRaisesRegex(APIHzError, "credentials_missing"):
            APIHzConfig.from_env({})

    def test_config_normalizes_optional_asset_hosts(self) -> None:
        config = APIHzConfig.from_env(
            {
                "APIHZ_ID": " 123456 ",
                "APIHZ_KEY": " secret-key ",
                "APIHZ_ASSET_HOSTS": " CDN.EXAMPLE.COM,cdn.example.com, img.example.cn ",
            }
        )
        self.assertEqual(config.developer_id, "123456")
        self.assertEqual(config.developer_key, "secret-key")
        self.assertEqual(config.extra_asset_hosts, ("cdn.example.com", "img.example.cn"))

    def test_config_rejects_control_characters(self) -> None:
        with self.assertRaisesRegex(APIHzError, "credentials_invalid"):
            APIHzConfig.from_env({"APIHZ_ID": "123\n456", "APIHZ_KEY": "secret"})


class APIHzQueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = APIHzConfig(developer_id="123456", developer_key="private-secret")

    def test_keyword_query_builds_expected_parameters(self) -> None:
        query = SearchQuery.create(words="大笑", page=2, limit=8, random=False)
        url = build_api_url(self.config, query)
        self.assertIn("type=2", url)
        self.assertIn("words=%E5%A4%A7%E7%AC%91", url)
        self.assertIn("page=2", url)
        self.assertIn("limit=8", url)

    def test_random_query_omits_keyword_and_page(self) -> None:
        query = SearchQuery.create(words="ignored", page=7, limit=3, random=True)
        url = build_api_url(self.config, query)
        self.assertIn("type=1", url)
        self.assertIn("limit=3", url)
        self.assertNotIn("words=", url)
        self.assertNotIn("page=", url)

    def test_query_rejects_invalid_keyword_and_limit(self) -> None:
        with self.assertRaisesRegex(APIHzError, "query_invalid"):
            SearchQuery.create(words="超过十个汉字的表情包搜索词", page=1, limit=10, random=False)
        with self.assertRaisesRegex(APIHzError, "query_invalid"):
            SearchQuery.create(words="大笑", page=1, limit=21, random=False)
        with self.assertRaisesRegex(APIHzError, "query_invalid"):
            SearchQuery.create(words="", page=1, limit=10, random=False)


class APIHzResponseTests(unittest.TestCase):
    def test_success_payload_returns_normalized_urls(self) -> None:
        payload = json.dumps(
            {
                "code": 200,
                "res": [
                    "https://res.apihz.cn/a.gif",
                    " https://res.apihz.cn/b.png ",
                ],
            }
        ).encode("utf-8")
        self.assertEqual(
            parse_api_response(payload),
            ("https://res.apihz.cn/a.gif", "https://res.apihz.cn/b.png"),
        )

    def test_api_error_does_not_expose_credentials(self) -> None:
        payload = '{"code":400,"msg":"通讯秘钥错误"}'.encode("utf-8")
        with self.assertRaisesRegex(APIHzError, "api_rejected") as raised:
            parse_api_response(payload)
        self.assertNotIn("private-secret", str(raised.exception))

    def test_rate_limit_message_has_stable_category(self) -> None:
        payload = '{"code":400,"msg":"请求过于频繁，请稍后重试"}'.encode("utf-8")
        with self.assertRaisesRegex(APIHzError, "rate_limited"):
            parse_api_response(payload)

    def test_malformed_or_empty_results_are_invalid(self) -> None:
        for payload in (b"not-json", b"[]", b'{"code":200,"res":[]}'):
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(APIHzError, "invalid_response"):
                    parse_api_response(payload)


class APIHzNetworkPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = APIHzConfig(developer_id="123456", developer_key="private-secret")
        self.public_resolver = lambda _host: ("8.8.8.8",)

    def test_url_policy_accepts_apihz_and_configured_public_hosts(self) -> None:
        self.assertEqual(validate_asset_url("https://res.apihz.cn/a.gif", self.config, self.public_resolver), "https://res.apihz.cn/a.gif")
        configured = replace(self.config, extra_asset_hosts=("cdn.example.com",))
        self.assertEqual(validate_asset_url("https://cdn.example.com/a.png", configured, self.public_resolver), "https://cdn.example.com/a.png")

    def test_url_policy_rejects_http_private_dns_and_unknown_host(self) -> None:
        with self.assertRaisesRegex(APIHzError, "unsafe_url"):
            validate_asset_url("http://res.apihz.cn/a.gif", self.config, self.public_resolver)
        with self.assertRaisesRegex(APIHzError, "unsafe_url"):
            validate_asset_url("https://res.apihz.cn/a.gif", self.config, lambda _host: ("127.0.0.1",))
        with self.assertRaisesRegex(APIHzError, "requires_host_configuration"):
            validate_asset_url("https://other.example/a.gif", self.config, self.public_resolver)

    def test_url_policy_rejects_credentials_fragments_and_custom_ports(self) -> None:
        unsafe = (
            "https://user@res.apihz.cn/a.gif",
            "https://res.apihz.cn:8443/a.gif",
            "https://res.apihz.cn/a.gif#fragment",
        )
        for url in unsafe:
            with self.subTest(url=url):
                with self.assertRaisesRegex(APIHzError, "unsafe_url"):
                    validate_asset_url(url, self.config, self.public_resolver)


class APIHzDownloadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = APIHzConfig(developer_id="123456", developer_key="private-secret")
        self.public_resolver = lambda _host: ("8.8.8.8",)

    def test_media_magic_distinguishes_supported_static_and_gif_formats(self) -> None:
        samples = {
            b"\xff\xd8\xff" + b"x" * 32: ("jpg", "image"),
            b"\x89PNG\r\n\x1a\n" + b"x" * 32: ("png", "image"),
            b"GIF89a" + b"x" * 32: ("gif", "gif"),
            b"RIFF" + b"\x00" * 4 + b"WEBP" + b"x" * 32: ("webp", "image"),
        }
        for payload, expected in samples.items():
            with self.subTest(expected=expected):
                self.assertEqual(detect_media_format(payload), expected)
        with self.assertRaisesRegex(APIHzError, "unsupported_media"):
            detect_media_format(b"<html>not an image</html>")

    def test_download_streams_valid_media_and_collapses_duplicate_bytes(self) -> None:
        gif = b"GIF89a" + b"animated-content" * 5

        def open_request(request: object, _timeout: float) -> MemoryResponse:
            return MemoryResponse(gif, url=request.full_url)

        with tempfile.TemporaryDirectory() as temp_dir:
            candidates, rejected = download_candidates(
                ("https://res.apihz.cn/first.gif", "https://res.apihz.cn/duplicate.gif"),
                Path(temp_dir), self.config, resolver=self.public_resolver, open_request=open_request,
            )
            self.assertEqual(len(candidates), 1)
            self.assertEqual(rejected, ())
            self.assertEqual(candidates[0]["asset_type"], "gif")
            self.assertEqual(candidates[0]["format"], "gif")
            self.assertTrue((Path(temp_dir) / candidates[0]["preview_path"]).is_file())

    def test_download_rejects_oversize_and_removes_partial_file(self) -> None:
        config = replace(self.config, max_bytes=12)
        png = b"\x89PNG\r\n\x1a\n" + b"x" * 32

        def open_request(request: object, _timeout: float) -> MemoryResponse:
            return MemoryResponse(png, url=request.full_url, headers={})

        with tempfile.TemporaryDirectory() as temp_dir:
            candidates, rejected = download_candidates(
                ("https://res.apihz.cn/large.png",), Path(temp_dir), config,
                resolver=self.public_resolver, open_request=open_request,
            )
            self.assertEqual(candidates, ())
            self.assertEqual(rejected[0]["category"], "file_too_large")
            self.assertEqual(list(Path(temp_dir).glob("*.part")), [])

    def test_redirect_result_is_revalidated_before_reading(self) -> None:
        def open_request(_request: object, _timeout: float) -> MemoryResponse:
            return MemoryResponse(b"GIF89a" + b"x" * 32, url="https://unknown.example/a.gif")

        with tempfile.TemporaryDirectory() as temp_dir:
            candidates, rejected = download_candidates(
                ("https://res.apihz.cn/a.gif",), Path(temp_dir), self.config,
                resolver=self.public_resolver, open_request=open_request,
            )
            self.assertEqual(candidates, ())
            self.assertEqual(rejected[0]["category"], "requires_host_configuration")

    def test_asset_download_retries_two_transient_open_failures(self) -> None:
        attempts = 0

        def open_request(request: object, _timeout: float) -> MemoryResponse:
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise URLError("temporary asset failure")
            return MemoryResponse(b"GIF89a" + b"x" * 32, url=request.full_url)

        with tempfile.TemporaryDirectory() as temp_dir:
            candidates, rejected = download_candidates(
                ("https://res.apihz.cn/retry.gif",), Path(temp_dir), self.config,
                resolver=self.public_resolver, open_request=open_request, sleep=lambda _delay: None,
            )
            self.assertEqual(len(candidates), 1)
            self.assertEqual(rejected, ())
            self.assertEqual(attempts, 3)
    def test_manifest_and_preview_use_only_local_image_sources(self) -> None:
        candidate = {
            "id": "media-aaaaaaaaaaaa", "provider": "apihz", "asset_type": "gif", "format": "gif",
            "preview_path": "candidates/media-aaaaaaaaaaaa.gif", "source_url": "https://res.apihz.cn/a.gif",
            "width": None, "height": None, "byte_size": 42, "sha256": "a" * 64,
            "rights_note": "source collected from the public web; publication rights not verified", "selected": False,
        }
        query = SearchQuery.create(words="大笑", page=1, limit=10)
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path, preview_path = write_search_artifacts(
                Path(temp_dir), search_id="search-bbbbbbbbbbbb", query=query,
                candidates=(candidate,), rejected=(), created_at="2026-07-20T00:00:00Z",
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            preview = preview_path.read_text(encoding="utf-8")
            self.assertEqual(manifest["candidates"][0]["asset_type"], "gif")
            self.assertIn('src="candidates/media-aaaaaaaaaaaa.gif"', preview)
            self.assertIn("GIF", preview)
            self.assertIn("publication rights not verified", preview)
            self.assertNotIn("private-secret", preview)
            self.assertNotIn('src="https://', preview)


class APIHzFetchTests(unittest.TestCase):
    def test_default_urlopen_wrapper_passes_timeout_as_keyword(self) -> None:
        sentinel = object()

        def fake_urlopen(request: object, data: object = None, *, timeout: float) -> object:
            self.assertIsNone(data)
            self.assertEqual(timeout, 15.0)
            return sentinel

        with patch("apihz_media.urlopen", side_effect=fake_urlopen):
            self.assertIs(open_url(object(), 15.0), sentinel)
    def test_fetch_retries_transient_failure_without_leaking_request_url(self) -> None:
        config = APIHzConfig(developer_id="123456", developer_key="private-secret", retries=2)
        query = SearchQuery.create(words="大笑", limit=1)
        attempts = 0

        def open_request(request: object, _timeout: float) -> MemoryResponse:
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise URLError("temporary network error")
            payload = b'{"code":200,"res":["https://res.apihz.cn/a.gif"]}'
            return MemoryResponse(payload, url=request.full_url)

        urls = fetch_api_urls(config, query, open_request=open_request, sleep=lambda _delay: None)
        self.assertEqual(urls, ("https://res.apihz.cn/a.gif",))
        self.assertEqual(attempts, 3)
if __name__ == "__main__":
    unittest.main()
