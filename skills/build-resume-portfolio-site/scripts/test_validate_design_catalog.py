from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
CATALOG_ROOT = SKILL_ROOT / "vendor" / "ui-ux-pro-max"
VALIDATOR_PATH = SCRIPT_DIR / "validate_design_catalog.py"


def load_validator():
    if not VALIDATOR_PATH.is_file():
        raise AssertionError(f"missing validator: {VALIDATOR_PATH}")
    spec = importlib.util.spec_from_file_location("validate_design_catalog", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("unable to load design catalog validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateDesignCatalogTests(unittest.TestCase):
    def test_vendored_catalog_is_complete_and_hashes_match(self) -> None:
        self.assertTrue(CATALOG_ROOT.is_dir(), f"missing catalog: {CATALOG_ROOT}")
        validator = load_validator()

        report = validator.validate_catalog(CATALOG_ROOT)

        self.assertTrue(report.ok, report.errors)
        self.assertEqual(report.catalog_version, "2.11.0")
        self.assertIn("data/styles.csv", report.checked_files)
        self.assertIn("data/stacks/react.csv", report.checked_files)

    def test_missing_license_is_invalid(self) -> None:
        self.assertTrue(CATALOG_ROOT.is_dir(), f"missing catalog: {CATALOG_ROOT}")
        validator = load_validator()
        with tempfile.TemporaryDirectory(dir=SCRIPT_DIR) as directory:
            copy = Path(directory) / "catalog"
            shutil.copytree(CATALOG_ROOT, copy)
            (copy / "LICENSE").unlink()

            report = validator.validate_catalog(copy)

        self.assertIn("missing_license", report.errors)
        self.assertFalse(report.ok)

    def test_modified_csv_fails_manifest_validation(self) -> None:
        self.assertTrue(CATALOG_ROOT.is_dir(), f"missing catalog: {CATALOG_ROOT}")
        validator = load_validator()
        with tempfile.TemporaryDirectory(dir=SCRIPT_DIR) as directory:
            copy = Path(directory) / "catalog"
            shutil.copytree(CATALOG_ROOT, copy)
            with (copy / "data" / "styles.csv").open("a", encoding="utf-8") as handle:
                handle.write("\nmodified")

            report = validator.validate_catalog(copy)

        self.assertTrue(
            any(error == "hash_mismatch: data/styles.csv" for error in report.errors),
            report.errors,
        )
        self.assertFalse(report.ok)


if __name__ == "__main__":
    unittest.main()
