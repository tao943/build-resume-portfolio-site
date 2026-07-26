from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE_SKILL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SOURCE_SKILL_ROOT.parents[1]
INSTALLED_SKILL_ROOT = SOURCE_SKILL_ROOT
PLUGIN_MANIFEST = REPOSITORY_ROOT / ".codex-plugin" / "plugin.json"


class MemoryResponse:
    def __init__(self, body: bytes, url: str) -> None:
        self._body = body
        self._offset = 0
        self._url = url
        self.status = 200
        self.headers = {"Content-Length": str(len(body))}

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


class InstalledAPIHzMediaTests(unittest.TestCase):
    def test_plugin_metadata_advertises_optional_media(self) -> None:
        manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "1.2.0")
        self.assertIn("optional-media", manifest["keywords"])
        description = manifest["description"].lower()
        self.assertIn("optional", description)
        self.assertIn("user-confirmed", description)
        self.assertIn("media search", description)

    def test_installed_skill_contains_apihz_runtime_resources(self) -> None:
        required = (
            "scripts/apihz_media.py",
            "scripts/import_media_selection.py",
            "prompts/11-search-optional-media.md",
            "references/apihz-media-schema.json",
            "references/apihz-media-contract.md",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((INSTALLED_SKILL_ROOT / relative).is_file(), relative)

    def test_installed_provider_preserves_animated_gif_candidate(self) -> None:
        script = INSTALLED_SKILL_ROOT / "scripts" / "apihz_media.py"
        scripts_dir = str(script.parent)
        sys.path.insert(0, scripts_dir)
        try:
            spec = importlib.util.spec_from_file_location("installed_apihz_media", script)
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader if spec else None)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            config = module.APIHzConfig(developer_id="123456", developer_key="secret")

            def open_request(request: object, _timeout: float) -> MemoryResponse:
                return MemoryResponse(b"GIF89a" + b"animated" * 8, request.full_url)

            with tempfile.TemporaryDirectory() as temp_dir:
                candidates, rejected = module.download_candidates(
                    ("https://res.apihz.cn/a.gif",),
                    Path(temp_dir),
                    config,
                    resolver=lambda _host: ("8.8.8.8",),
                    open_request=open_request,
                )
        finally:
            sys.path.remove(scripts_dir)
        self.assertEqual(rejected, ())
        self.assertEqual(candidates[0]["format"], "gif")
        self.assertEqual(candidates[0]["asset_type"], "gif")


if __name__ == "__main__":
    unittest.main()
