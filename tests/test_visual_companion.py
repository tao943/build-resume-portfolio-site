from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VISUAL_ROOT = (
    ROOT
    / "skills"
    / "build-resume-portfolio-site"
    / "scripts"
    / "visual_companion"
)
SERVER = VISUAL_ROOT / "server.cjs"
NODE = shutil.which("node")


@unittest.skipUnless(NODE, "Node.js is required for visual companion tests")
class VisualCompanionServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.session = Path(self.temp.name).resolve()
        self.gallery = self.session / "gallery.html"
        self.gallery.write_text(
            "<!doctype html><html><body><h1>Directions</h1></body></html>",
            encoding="utf-8",
        )
        assets = self.session / "assets"
        assets.mkdir()
        (assets / "sample.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"></svg>',
            encoding="utf-8",
        )
        self.token = "test-token-1234567890"
        self.process = subprocess.Popen(
            [
                NODE,
                str(SERVER),
                "--session-dir",
                str(self.session),
                "--gallery",
                str(self.gallery),
                "--port",
                "0",
                "--token",
                self.token,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert self.process.stdout is not None
        startup_line = self.process.stdout.readline()
        if not startup_line:
            stderr = ""
            if self.process.stderr is not None:
                stderr = self.process.stderr.read()
            self.fail(f"server did not start: {stderr}")
        self.info = json.loads(startup_line)

    def tearDown(self) -> None:
        if hasattr(self, "process") and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=5)
        if hasattr(self, "process"):
            if self.process.stdout is not None:
                self.process.stdout.close()
            if self.process.stderr is not None:
                self.process.stderr.close()
        self.temp.cleanup()

    def open(
        self,
        path: str = "/",
        *,
        key: str | None = None,
        method: str = "GET",
        data: bytes | None = None,
    ):
        query_key = self.token if key is None else key
        url = (
            f"http://127.0.0.1:{self.info['port']}{path}"
            f"?key={urllib.parse.quote(query_key)}"
        )
        request = urllib.request.Request(url, method=method, data=data)
        return urllib.request.urlopen(request, timeout=3)

    def test_authenticated_get_serves_gallery_with_security_headers(
        self,
    ) -> None:
        with self.open() as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"Directions", response.read())
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertEqual(
                response.headers["X-Content-Type-Options"],
                "nosniff",
            )
            self.assertEqual(response.headers["X-Frame-Options"], "DENY")
            self.assertEqual(
                response.headers["Referrer-Policy"],
                "no-referrer",
            )
            self.assertEqual(
                response.headers["Cross-Origin-Resource-Policy"],
                "same-origin",
            )
            self.assertIn(
                "default-src 'self'",
                response.headers["Content-Security-Policy"],
            )

    def test_missing_or_wrong_key_is_forbidden(self) -> None:
        base = f"http://127.0.0.1:{self.info['port']}/"
        for url in (base, f"{base}?key=wrong"):
            with self.subTest(url=url):
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(url, timeout=3)
                self.assertEqual(caught.exception.code, 403)

    def test_head_returns_headers_without_body(self) -> None:
        with self.open(method="HEAD") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), b"")
            self.assertIn("text/html", response.headers["Content-Type"])

    def test_write_methods_are_rejected(self) -> None:
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            with self.subTest(method=method):
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    self.open(method=method, data=b"x")
                self.assertEqual(caught.exception.code, 405)
                self.assertEqual(caught.exception.headers["Allow"], "GET, HEAD")

    def test_local_asset_uses_expected_mime_type(self) -> None:
        with self.open("/files/assets/sample.svg") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Content-Type"], "image/svg+xml")

    def test_traversal_and_unsupported_files_are_not_served(self) -> None:
        (self.session.parent / "secret.txt").write_text(
            "secret",
            encoding="utf-8",
        )
        (self.session / "payload.exe").write_bytes(b"MZ")
        for path in (
            "/files/%2e%2e/secret.txt",
            "/files/payload.exe",
            "/files/missing.svg",
        ):
            with self.subTest(path=path):
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    self.open(path)
                self.assertEqual(caught.exception.code, 404)

    def test_server_defaults_to_loopback(self) -> None:
        self.assertEqual(self.info["host"], "127.0.0.1")
        self.assertTrue(self.info["url"].startswith("http://127.0.0.1:"))


if __name__ == "__main__":
    unittest.main()
