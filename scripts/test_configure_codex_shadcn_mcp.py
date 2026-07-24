from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from configure_codex_shadcn_mcp import ensure_shadcn_mcp


class ConfigureCodexShadcnMcpTests(unittest.TestCase):
    def test_adds_shadcn_server_without_changing_existing_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            path.write_text('model = "gpt-5"\n\n[desktop]\ntheme = "dark"\n', encoding="utf-8")

            result = ensure_shadcn_mcp(path)

            text = path.read_text(encoding="utf-8")
            self.assertTrue(result.changed)
            self.assertIn('model = "gpt-5"', text)
            self.assertIn('[desktop]', text)
            self.assertIn('[mcp_servers.shadcn]', text)
            self.assertIn('command = "npx"', text)
            self.assertIn('args = ["shadcn@latest", "mcp"]', text)

    def test_updates_existing_shadcn_block_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            path.write_text(
                '[mcp_servers.shadcn]\ncommand = "old"\nargs = ["old"]\n\n[desktop]\ntheme = "dark"\n',
                encoding="utf-8",
            )

            first = ensure_shadcn_mcp(path)
            second = ensure_shadcn_mcp(path)

            text = path.read_text(encoding="utf-8")
            self.assertTrue(first.changed)
            self.assertFalse(second.changed)
            self.assertEqual(text.count("[mcp_servers.shadcn]"), 1)
            self.assertIn('[desktop]', text)


if __name__ == "__main__":
    unittest.main()
