from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capture_site import (
    PLAYWRIGHT_INSTALL_COMMANDS,
    VIEWPORTS,
    PlaywrightDependencyError,
    capture_site,
    prepare_capture_paths,
)


class CaptureSiteTests(unittest.TestCase):
    def test_viewports_match_the_workflow_contract(self) -> None:
        self.assertEqual(
            VIEWPORTS,
            {
                "desktop": {"width": 1440, "height": 900},
                "tablet": {"width": 1024, "height": 768},
                "mobile": {"width": 390, "height": 844},
            },
        )

    def test_missing_html_is_rejected_before_browser_loading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                capture_site(Path(directory) / "missing.html", Path(directory) / "shots")

    def test_prepare_capture_paths_creates_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            html_path = root / "site.html"
            html_path.write_text("<!doctype html>", encoding="utf-8")
            output_dir = root / "screenshots"

            resolved_html, resolved_output = prepare_capture_paths(html_path, output_dir)

            self.assertEqual(resolved_html, html_path.resolve())
            self.assertEqual(resolved_output, output_dir.resolve())
            self.assertTrue(output_dir.is_dir())

    def test_dependency_error_contains_install_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            html_path = root / "site.html"
            html_path.write_text("<!doctype html>", encoding="utf-8")

            with patch("capture_site._load_sync_playwright", side_effect=PlaywrightDependencyError()):
                with self.assertRaises(PlaywrightDependencyError) as caught:
                    capture_site(html_path, root / "shots")

            message = str(caught.exception)
            for command in PLAYWRIGHT_INSTALL_COMMANDS:
                self.assertIn(command, message)


if __name__ == "__main__":
    unittest.main()
