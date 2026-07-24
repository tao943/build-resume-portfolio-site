from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from index_reference_library import index_reference_library


def write_image(path: Path, size: tuple[int, int], color: tuple[int, int, int]) -> None:
    from PIL import Image

    image = Image.new("RGB", size, color)
    image.save(path, format="PNG")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IndexReferenceLibraryTests(unittest.TestCase):
    def test_indexes_images_without_modifying_sources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "references"
            source.mkdir()
            first = source / "wide.png"
            second = source / "portrait.jpg"
            write_image(first, (1200, 800), (20, 40, 80))
            from PIL import Image

            Image.new("RGB", (600, 1000), (120, 80, 40)).save(second, format="JPEG")
            before = {path.name: sha256(path) for path in source.iterdir()}

            report = index_reference_library(source, root, page_size=9, thumbnail_edge=160)

            self.assertTrue(report.ok)
            self.assertTrue(report.ready)
            self.assertEqual(report.valid_count, 2)
            manifest_path = root / ".resume-site-work" / "reference-library" / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["library_status"], "ready")
            self.assertEqual(len(manifest["references"]), 2)
            self.assertTrue(all(item["usage_scope"] == "style_only" for item in manifest["references"]))
            self.assertTrue(all(item["selectable"] for item in manifest["references"]))
            self.assertTrue(all((manifest_path.parent / item["path"]).is_file() for item in manifest["references"]))
            self.assertTrue(report.contact_sheets)
            self.assertTrue(all(Path(path).is_file() for path in report.contact_sheets))
            self.assertEqual(before, {path.name: sha256(path) for path in source.iterdir()})
            self.assertFalse((root / ".resume-site-work" / "reference-library" / "originals").exists())

    def test_rebuild_is_idempotent_and_keeps_version_for_same_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "references"
            source.mkdir()
            write_image(source / "one.png", (400, 300), (1, 2, 3))

            first = index_reference_library(source, root, thumbnail_edge=120)
            first_manifest = json.loads(Path(first.manifest_path).read_text(encoding="utf-8"))
            second = index_reference_library(source, root, thumbnail_edge=120)
            second_manifest = json.loads(Path(second.manifest_path).read_text(encoding="utf-8"))

            self.assertFalse(second.changed)
            self.assertEqual(first_manifest["library_version"], second_manifest["library_version"])
            self.assertEqual(first_manifest["catalog_fingerprint"], second_manifest["catalog_fingerprint"])

    def test_exact_duplicate_is_listed_but_not_selectable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "references"
            source.mkdir()
            original = source / "a.png"
            duplicate = source / "b.png"
            write_image(original, (300, 200), (10, 20, 30))
            duplicate.write_bytes(original.read_bytes())

            report = index_reference_library(source, root)
            manifest = json.loads(Path(report.manifest_path).read_text(encoding="utf-8"))
            records = {item["source_path"].split("/")[-1]: item for item in manifest["references"]}
            self.assertEqual(report.duplicate_count, 1)
            self.assertTrue(records["a.png"]["selectable"])
            self.assertFalse(records["b.png"]["selectable"])
            self.assertEqual(records["b.png"]["duplicate_of"], records["a.png"]["id"])

    def test_corrupt_and_unsupported_files_are_warnings_when_valid_images_exist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "references"
            source.mkdir()
            write_image(source / "valid.png", (300, 200), (1, 2, 3))
            (source / "broken.jpg").write_bytes(b"not an image")
            (source / "notes.txt").write_text("ignore", encoding="utf-8")

            report = index_reference_library(source, root)

            self.assertTrue(report.ok)
            self.assertEqual(report.valid_count, 1)
            self.assertTrue(any("broken.jpg" in warning for warning in report.warnings))
            self.assertTrue(any("notes.txt" in warning for warning in report.warnings))

    def test_empty_source_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "references"
            source.mkdir()

            report = index_reference_library(source, root)

            self.assertFalse(report.ok)
            self.assertFalse(report.ready)
            self.assertEqual(report.valid_count, 0)

    def test_rejects_output_inside_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "references"
            source.mkdir()
            write_image(source / "valid.png", (300, 200), (1, 2, 3))

            with self.assertRaises(ValueError):
                index_reference_library(source, source / ".resume-site-work")


if __name__ == "__main__":
    unittest.main()
