from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from snapshot_vite_project import restore_snapshot, snapshot_project


def write_source(root: Path) -> None:
    (root / "src").mkdir(parents=True)
    (root / "src" / "App.jsx").write_text("prototype", encoding="utf-8")
    (root / "package.json").write_text("{}", encoding="utf-8")
    for ignored in ("node_modules", "dist", ".git", ".resume-site-work"):
        path = root / ignored
        path.mkdir()
        (path / "ignored.txt").write_text("ignored", encoding="utf-8")


class SnapshotViteProjectTests(unittest.TestCase):
    def test_snapshot_copies_source_and_excludes_generated_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "site"
            destination = root / "versions" / "v1-prototype"
            write_source(source)
            report = snapshot_project(source, destination)
            self.assertTrue(report.ok)
            self.assertEqual((destination / "src" / "App.jsx").read_text(encoding="utf-8"), "prototype")
            for ignored in ("node_modules", "dist", ".git", ".resume-site-work"):
                self.assertFalse((destination / ignored).exists())

    def test_snapshot_never_overwrites_an_existing_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "site"
            destination = root / "versions" / "v1-prototype"
            write_source(source)
            snapshot_project(source, destination)
            with self.assertRaises(FileExistsError):
                snapshot_project(source, destination)

    def test_snapshot_rejects_overlapping_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "site"
            write_source(source)
            with self.assertRaises(ValueError):
                snapshot_project(source, source / "versions" / "v1")
            with self.assertRaises(ValueError):
                snapshot_project(source, source)

    def test_restore_atomically_replaces_the_editable_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "site"
            snapshot = root / "versions" / "v1-prototype"
            write_source(source)
            snapshot_project(source, snapshot)
            (source / "src" / "App.jsx").write_text("broken", encoding="utf-8")
            (source / "stale.txt").write_text("stale", encoding="utf-8")
            report = restore_snapshot(snapshot, source)
            self.assertTrue(report.ok)
            self.assertEqual((source / "src" / "App.jsx").read_text(encoding="utf-8"), "prototype")
            self.assertFalse((source / "stale.txt").exists())


if __name__ == "__main__":
    unittest.main()