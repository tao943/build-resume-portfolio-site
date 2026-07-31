from __future__ import annotations

import json
import os
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
LAUNCH = VISUAL_ROOT / "launch.cjs"
STOP = VISUAL_ROOT / "stop.cjs"
GALLERY_SHELL = (
    ROOT
    / "skills"
    / "build-resume-portfolio-site"
    / "assets"
    / "visual-companion"
    / "gallery-shell.html"
)
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

    def test_health_identifies_the_exact_server_instance(self) -> None:
        with self.open("/health") as response:
            payload = json.loads(response.read())
        self.assertEqual(payload["pid"], self.info["pid"])
        self.assertEqual(
            Path(payload["session_dir"]).resolve(),
            self.session,
        )


@unittest.skipUnless(NODE, "Node.js is required for visual companion tests")
class VisualCompanionLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = (Path(self.temp.name) / "workspace").resolve()
        self.workspace.mkdir()
        self.source = Path(self.temp.name) / "source"
        self.source.mkdir()
        self.gallery = self.source / "gallery.html"
        self.gallery.write_text(
            "<!doctype html><h1>Portable directions</h1>",
            encoding="utf-8",
        )
        assets = self.source / "assets"
        assets.mkdir()
        (assets / "mark.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"></svg>',
            encoding="utf-8",
        )
        self.sessions: list[dict] = []

    def tearDown(self) -> None:
        for info in self.sessions:
            subprocess.run(
                [
                    NODE,
                    str(STOP),
                    "--workspace-root",
                    str(self.workspace),
                    "--server-info",
                    info["server_info"],
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
        self.temp.cleanup()

    def launch(
        self,
        *,
        open_browser: bool = False,
        extra_env: dict[str, str] | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        command = [
            NODE,
            str(LAUNCH),
            "--workspace-root",
            str(self.workspace),
            "--gallery",
            str(self.gallery),
        ]
        if open_browser:
            command.append("--open")
        environment = os.environ.copy()
        environment.update(extra_env or {})
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
            env=environment,
        )
        info = json.loads(result.stdout.splitlines()[0]) if result.stdout else {}
        if info.get("server_info"):
            self.sessions.append(info)
        return result, info

    def test_launch_creates_contained_session_and_server_info(self) -> None:
        result, info = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        session = Path(info["session_dir"]).resolve()
        expected = (
            self.workspace
            / ".resume-site-work"
            / "style-preview"
            / "sessions"
        ).resolve()
        self.assertTrue(session.is_relative_to(expected))
        self.assertEqual(
            Path(info["server_info"]).resolve(),
            session / "state" / "server-info.json",
        )
        self.assertTrue(Path(info["server_info"]).is_file())
        self.assertTrue((session / "gallery.html").is_file())
        self.assertTrue((session / "assets" / "mark.svg").is_file())
        with urllib.request.urlopen(info["url"], timeout=3) as response:
            self.assertIn(b"Portable directions", response.read())

    def test_open_failure_does_not_stop_server(self) -> None:
        result, info = self.launch(
            open_browser=True,
            extra_env={
                "VISUAL_COMPANION_OPEN_COMMAND":
                    "__missing_visual_open_command__"
            },
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(info["open_warning"], "OPEN_FAILED")
        with urllib.request.urlopen(info["url"], timeout=3) as response:
            self.assertEqual(response.status, 200)

    def test_stop_terminates_verified_session_and_keeps_gallery(self) -> None:
        _, info = self.launch()
        session = Path(info["session_dir"])
        result = subprocess.run(
            [
                NODE,
                str(STOP),
                "--workspace-root",
                str(self.workspace),
                "--server-info",
                info["server_info"],
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        self.sessions.remove(info)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["type"], "server-stopped")
        self.assertTrue((session / "gallery.html").is_file())
        with self.assertRaises((urllib.error.URLError, TimeoutError)):
            urllib.request.urlopen(info["url"], timeout=1)

    def test_stop_rejects_server_info_outside_workspace(self) -> None:
        outside = Path(self.temp.name) / "outside.json"
        outside.write_text(
            json.dumps({"pid": os.getpid()}),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                NODE,
                str(STOP),
                "--workspace-root",
                str(self.workspace),
                "--server-info",
                str(outside),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("INVALID_SESSION_PATH", result.stderr)


class VisualCompanionPackageTests(unittest.TestCase):
    def test_gallery_shell_is_display_only(self) -> None:
        text = GALLERY_SHELL.read_text(encoding="utf-8").lower()
        self.assertNotIn("<form", text)
        self.assertNotIn("data-choice", text)
        self.assertNotIn("<button", text)
        self.assertIn("approve in the conversation", text)
        self.assertIn("<!-- visual-directions -->", text)

    def test_visual_companion_resources_are_packaged(self) -> None:
        skill_root = ROOT / "skills" / "build-resume-portfolio-site"
        required = (
            "assets/visual-companion/gallery-shell.html",
            "references/visual-style-preview-contract.md",
            "scripts/visual_companion/server.cjs",
            "scripts/visual_companion/launch.cjs",
            "scripts/visual_companion/stop.cjs",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((skill_root / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
