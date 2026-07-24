from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from import_media_selection import (  # noqa: E402
    SelectionError,
    import_selected_media,
)


RIGHTS_NOTE = "source collected from the public web; publication rights not verified"


class ImportMediaSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary.name)
        self.search_root = (
            self.workspace
            / ".resume-site-work"
            / "media-search"
            / "search-aaaaaaaaaaaa"
        )
        self.candidates_dir = self.search_root / "candidates"
        self.candidates_dir.mkdir(parents=True)

        self.gif = b"GIF89a" + b"animated" * 8
        self.png = b"\x89PNG\r\n\x1a\n" + b"static" * 8
        self.gif_path = self.candidates_dir / "media-goodgif.gif"
        self.png_path = self.candidates_dir / "media-other.png"
        self.gif_path.write_bytes(self.gif)
        self.png_path.write_bytes(self.png)
        self.manifest = self.search_root / "manifest.json"
        self._write_manifest()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _candidate(
        self,
        candidate_id: str,
        path: Path,
        media_format: str,
        asset_type: str,
        payload: bytes,
    ) -> dict[str, object]:
        return {
            "id": candidate_id,
            "provider": "apihz",
            "asset_type": asset_type,
            "format": media_format,
            "preview_path": f"candidates/{path.name}",
            "source_url": f"https://res.apihz.cn/{path.name}",
            "width": None,
            "height": None,
            "byte_size": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "rights_note": RIGHTS_NOTE,
            "selected": False,
        }

    def _write_manifest(self) -> None:
        manifest = {
            "schema_version": 1,
            "search_id": "search-aaaaaaaaaaaa",
            "provider": "apihz",
            "query": {"mode": "keyword", "words": "大笑", "page": 1, "limit": 10},
            "created_at": "2026-07-20T00:00:00Z",
            "candidates": [
                self._candidate("media-goodgif", self.gif_path, "gif", "gif", self.gif),
                self._candidate("media-other", self.png_path, "png", "image", self.png),
            ],
            "rejected": [],
            "rights_note": RIGHTS_NOTE,
        }
        self.manifest.write_text(json.dumps(manifest), encoding="utf-8")

    def test_import_copies_only_selected_verified_candidates(self) -> None:
        report = import_selected_media(
            self.workspace,
            self.manifest,
            ("media-goodgif",),
            updated_at="2026-07-20T01:00:00Z",
        )
        self.assertEqual(
            [item["candidate_id"] for item in report["assets"]],
            ["media-goodgif"],
        )
        imported = (
            self.workspace
            / ".resume-site-work"
            / "site"
            / "public"
            / "assets"
            / "external"
            / "media-goodgif.gif"
        )
        self.assertEqual(imported.read_bytes(), self.gif)
        self.assertFalse(imported.with_name("media-other.png").exists())
        self.assertEqual(report["assets"][0]["project_path"], "/assets/external/media-goodgif.gif")

    def test_import_rejects_unknown_and_empty_selection(self) -> None:
        for selection in ((), ("missing",)):
            with self.subTest(selection=selection):
                with self.assertRaisesRegex(SelectionError, "selection_invalid"):
                    import_selected_media(self.workspace, self.manifest, selection)

    def test_import_rejects_traversal_candidate_path(self) -> None:
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        manifest["candidates"][0]["preview_path"] = "../outside.gif"
        self.manifest.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(SelectionError, "selection_invalid"):
            import_selected_media(self.workspace, self.manifest, ("media-goodgif",))

    def test_import_rejects_candidate_modified_after_manifest(self) -> None:
        self.gif_path.write_bytes(self.gif + b"changed")
        with self.assertRaisesRegex(SelectionError, "selection_invalid"):
            import_selected_media(self.workspace, self.manifest, ("media-goodgif",))

    def test_import_is_idempotent_and_preserves_earlier_selections(self) -> None:
        import_selected_media(
            self.workspace,
            self.manifest,
            ("media-goodgif",),
            updated_at="2026-07-20T01:00:00Z",
        )
        report = import_selected_media(
            self.workspace,
            self.manifest,
            ("media-other", "media-goodgif"),
            updated_at="2026-07-20T02:00:00Z",
        )
        self.assertEqual(
            [item["candidate_id"] for item in report["assets"]],
            ["media-goodgif", "media-other"],
        )
        report_path = self.workspace / ".resume-site-work" / "reports" / "media-selection.json"
        self.assertEqual(json.loads(report_path.read_text(encoding="utf-8")), report)


if __name__ == "__main__":
    unittest.main()
