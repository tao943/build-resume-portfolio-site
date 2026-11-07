from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
import urllib.request
from pathlib import Path


NODE = shutil.which("node")
SCRIPTS = Path(__file__).resolve().parent / "visual_companion"


@unittest.skipUnless(NODE, "Node.js is required for the real preview-session test")
class PreviewReuseTests(unittest.TestCase):
    def test_gallery_refresh_keeps_url_pid_and_does_not_open_browser(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            gallery = root / "draft.html"
            gallery.write_text("<h1>First design</h1>", encoding="utf-8")
            args = [NODE, str(SCRIPTS / "launch.cjs"), "--workspace-root", str(root), "--gallery", str(gallery)]
            started = subprocess.run(args, capture_output=True, text=True, timeout=10)
            self.assertEqual(started.returncode, 0, started.stderr)
            info = json.loads(started.stdout)
            try:
                gallery.write_text("<h1>Revised design</h1>", encoding="utf-8")
                env = dict(os.environ, VISUAL_COMPANION_OPEN_COMMAND=str(root / "must-not-open"))
                updated = subprocess.run(args + ["--reuse-session", info["server_info"], "--open"], env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(updated.returncode, 0, updated.stderr)
                after = json.loads(updated.stdout)
                self.assertEqual(after["url"], info["url"])
                self.assertEqual(after["pid"], info["pid"])
                self.assertTrue(after["reused"])
                self.assertIsNone(after["open_warning"])
                with urllib.request.urlopen(after["url"], timeout=3) as response:
                    self.assertIn("Revised design", response.read().decode())
                self.assertEqual(len(list((root / ".resume-site-work/style-preview/sessions").iterdir())), 1)
                foreign = root / "server-info.json"
                foreign.write_text(json.dumps(info), encoding="utf-8")
                refused = subprocess.run(args + ["--reuse-session", str(foreign)], capture_output=True, text=True, timeout=10)
                self.assertNotEqual(refused.returncode, 0)
            finally:
                subprocess.run([NODE, str(SCRIPTS / "stop.cjs"), "--workspace-root", str(root), "--server-info", info["server_info"]], capture_output=True, text=True, timeout=10)


if __name__ == "__main__":
    unittest.main()
