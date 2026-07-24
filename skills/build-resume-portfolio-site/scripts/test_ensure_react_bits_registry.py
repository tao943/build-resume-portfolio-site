from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ensure_react_bits_registry import ensure_registry


class EnsureReactBitsRegistryTests(unittest.TestCase):
    def test_creates_components_json_for_javascript_vite_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src" / "main.jsx").write_text("export default {}", encoding="utf-8")

            result = ensure_registry(root)

            config = json.loads((root / "components.json").read_text(encoding="utf-8"))
            self.assertTrue(result.changed)
            self.assertFalse(config["tsx"])
            self.assertEqual(
                config["registries"]["@react-bits"],
                "https://reactbits.dev/r/{name}.json",
            )
            self.assertEqual(config["aliases"]["components"], "@/components")

    def test_preserves_existing_configuration_and_other_registries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            existing = {
                "$schema": "https://ui.shadcn.com/schema.json",
                "style": "vega",
                "tsx": True,
                "aliases": {"components": "~/ui"},
                "registries": {"@internal": "https://example.test/{name}.json"},
                "custom": {"keep": True},
            }
            (root / "components.json").write_text(json.dumps(existing), encoding="utf-8")

            ensure_registry(root)

            config = json.loads((root / "components.json").read_text(encoding="utf-8"))
            self.assertEqual(config["style"], "vega")
            self.assertEqual(config["aliases"]["components"], "~/ui")
            self.assertEqual(config["registries"]["@internal"], "https://example.test/{name}.json")
            self.assertTrue(config["custom"]["keep"])
            self.assertEqual(
                config["registries"]["@react-bits"],
                "https://reactbits.dev/r/{name}.json",
            )

    def test_second_run_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src" / "main.tsx").write_text("export default {}", encoding="utf-8")

            first = ensure_registry(root)
            second = ensure_registry(root)

            self.assertTrue(first.changed)
            self.assertFalse(second.changed)
            self.assertTrue(second.tsx)

    def test_rejects_non_vite_source_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "missing Vite src directory"):
                ensure_registry(Path(directory))


if __name__ == "__main__":
    unittest.main()
