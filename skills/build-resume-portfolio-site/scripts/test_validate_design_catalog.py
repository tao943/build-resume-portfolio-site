from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from validate_design_catalog import validate_catalog


CATALOG = Path(__file__).resolve().parents[1] / "vendor" / "ui-ux-pro-max"


class DesignCatalogIntegrityTests(unittest.TestCase):
    def test_bundled_catalog_is_valid(self) -> None:
        report = validate_catalog(CATALOG)
        self.assertTrue(report.ok, report.errors)

    def test_line_ending_conversion_preserves_integrity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            catalog = Path(directory) / "catalog"
            shutil.copytree(CATALOG, catalog)
            styles = catalog / "data" / "styles.csv"
            styles.write_bytes(styles.read_bytes().replace(b"\n", b"\r\n"))

            report = validate_catalog(catalog)
            self.assertTrue(report.ok, report.errors)

            styles.write_bytes(styles.read_bytes().replace(b"\r\n", b"\n") + b"changed\n")
            report = validate_catalog(catalog)
            self.assertIn("hash_mismatch: data/styles.csv", report.errors)


if __name__ == "__main__":
    unittest.main()
