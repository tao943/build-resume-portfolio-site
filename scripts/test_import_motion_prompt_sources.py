from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from import_motion_prompt_sources import (
    SOURCE_IDS,
    split_prompt_sources,
    write_prompt_sources,
)


class ImportMotionPromptSourcesTests(unittest.TestCase):
    def test_split_preserves_all_blocks_and_duplicate_original_number(self) -> None:
        text = "intro\n1、 first\n7、 seventh-a\n7、 seventh-b\n10、 tenth\n"
        source_ids = ("one", "seven-a", "seven-b", "ten")

        sources = split_prompt_sources(text, source_ids=source_ids)

        self.assertEqual([item.source_id for item in sources], list(source_ids))
        self.assertEqual([item.original_number for item in sources], [1, 7, 7, 10])
        self.assertEqual(sources[2].body, "7、 seventh-b")

    def test_writer_creates_one_utf8_markdown_file_per_source(self) -> None:
        text = "1、 alpha\n2、 beta\n"
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            output_dir = Path(directory)
            sources = split_prompt_sources(text, source_ids=("01-alpha", "02-beta"))

            written = write_prompt_sources(sources, output_dir)

            self.assertEqual(len(written), 2)
            first = written[0].read_text(encoding="utf-8")
            self.assertIn("source_id: 01-alpha", first)
            self.assertIn("original_number: 1", first)
            self.assertIn("usage_scope: motion-recipe-source-only", first)
            self.assertTrue(first.endswith("1、 alpha\n"))

    def test_catalog_source_ids_are_stable_and_complete(self) -> None:
        self.assertEqual(len(SOURCE_IDS), 11)
        self.assertEqual(SOURCE_IDS[0], "01-minimalist-3d-ribbon")
        self.assertEqual(SOURCE_IDS[-1], "11-assist-floating-cards")


if __name__ == "__main__":
    unittest.main()
