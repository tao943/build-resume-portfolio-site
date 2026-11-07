from __future__ import annotations

import unittest
from unittest.mock import patch

from check_environment import inspect_environment


def command(name):
    versions = {"node": "v24.1.0", "npm": "11.0.0"}
    return {"available": name in versions, "path": f"/local/{name}" if name in versions else None,
            "version": versions.get(name)}


class EnvironmentTests(unittest.TestCase):
    @patch("check_environment.sys.version_info", (3, 11, 0))
    @patch("check_environment._command", side_effect=command)
    @patch("check_environment.importlib.util.find_spec", return_value=None)
    def test_optional_tools_do_not_block_core(self, *_):
        report = inspect_environment()
        self.assertEqual(report["status"], "ready")
        self.assertFalse(report["capabilities"]["pdf_export"])
        self.assertFalse(report["capabilities"]["scanned_pdf_ocr"])
        self.assertTrue(all(item["action"] for item in report["checks"] if not item["available"]))

    @patch("check_environment.sys.version_info", (3, 11, 0))
    @patch("check_environment._command", side_effect=command)
    @patch("check_environment.importlib.util.find_spec", return_value=None)
    def test_required_pdf_dependencies_block_with_actions(self, *_):
        report = inspect_environment(["pdf-export"])
        self.assertEqual(report["status"], "blocked")
        required_missing = {item["name"] for item in report["checks"] if item["required"] and not item["available"]}
        self.assertEqual(required_missing, {"reportlab", "pypdf"})

    @patch("check_environment.sys.version_info", (3, 11, 0))
    @patch("check_environment.importlib.util.find_spec", return_value=True)
    def test_older_node_and_missing_npm_are_reported(self, *_):
        def old_command(name):
            return {"available": name == "node", "path": "/local/node" if name == "node" else None,
                    "version": "v20.19.0" if name == "node" else None}
        with patch("check_environment._command", side_effect=old_command):
            report = inspect_environment()
        self.assertEqual(report["status"], "blocked")
        missing = {item["name"] for item in report["checks"] if item["required"] and not item["available"]}
        self.assertEqual(missing, {"node", "npm"})


if __name__ == "__main__":
    unittest.main()
