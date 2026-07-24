from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_vite_project import validate_vite_project


PACKAGE = {
    "scripts": {"dev": "vite", "build": "vite build"},
    "dependencies": {"react": "^19.0.0", "react-dom": "^19.0.0"},
    "devDependencies": {"vite": "^7.0.0"},
}

INDEX = """<!doctype html><html><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>Portfolio</title></head><body><div id=\"root\"></div><script type=\"module\" src=\"/src/main.jsx\"></script></body></html>"""

APP = """
import './styles.css'
export default function App() {
  return <main>
    <section id=\"hero\"><h1>Hero</h1></section>
    <section id=\"experience\"><h2>个人经历</h2></section>
    <section id=\"projects\"><h2>精选项目</h2></section>
    <section id=\"strengths\"><h2>个人优势</h2></section>
    <section id=\"contact\"><h2>联系方式</h2></section>
  </main>
}
"""

MAIN = """import React from 'react'; import { createRoot } from 'react-dom/client'; import App from './App.jsx'; createRoot(document.getElementById('root')).render(<App />);"""

CSS = """:root { --content-max: 1700px; } :focus-visible { outline: 2px solid currentColor; } @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; } }"""

POSTER_MEDIA = """
function AdaptiveMotionMedia({ poster = '/motion/poster.webp', video }) {
  return <div data-motion-media className="motion-media">
    {video ? <video autoPlay muted loop playsInline preload="metadata" poster={poster}
      onError={(event) => event.currentTarget.hidden = true}><source src={video} /></video> : null}
    <img src={poster} alt="" aria-hidden="true" />
  </div>
}
"""

VIDEO_MEDIA = POSTER_MEDIA + "\nconst upgradedVideo = '/motion/hero.webm';"


def write_project(root: Path) -> None:
    (root / "src").mkdir(parents=True)
    (root / "package.json").write_text(json.dumps(PACKAGE), encoding="utf-8")
    (root / "index.html").write_text(INDEX, encoding="utf-8")
    (root / "src" / "main.jsx").write_text(MAIN, encoding="utf-8")
    (root / "src" / "App.jsx").write_text(APP, encoding="utf-8")
    (root / "src" / "styles.css").write_text(CSS, encoding="utf-8")


class ValidateViteProjectTests(unittest.TestCase):
    def test_accepts_minimal_valid_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            report = validate_vite_project(root, "prototype")
            self.assertTrue(report.ok, report.errors)

    def test_rejects_missing_build_script(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            package = dict(PACKAGE)
            package["scripts"] = {"dev": "vite"}
            (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
            report = validate_vite_project(root, "prototype")
            self.assertIn("missing_build_script", report.errors)

    def test_rejects_missing_react_or_vite_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            package = dict(PACKAGE)
            package["dependencies"] = {"react": "^19.0.0"}
            package["devDependencies"] = {}
            (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
            report = validate_vite_project(root, "prototype")
            self.assertIn("missing_dependency: react-dom", report.errors)
            self.assertIn("missing_dependency: vite", report.errors)

    def test_rejects_missing_root_mount_or_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            (root / "index.html").write_text("<!doctype html><html><body></body></html>", encoding="utf-8")
            report = validate_vite_project(root, "prototype")
            self.assertIn("missing_root_mount", report.errors)
            self.assertIn("missing_module_entry", report.errors)

    def test_rejects_missing_required_page_region(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            (root / "src" / "App.jsx").write_text(APP.replace('id=\"strengths\"', 'id=\"other\"').replace("个人优势", "其他"), encoding="utf-8")
            report = validate_vite_project(root, "prototype")
            self.assertIn("missing_page_region: strengths", report.errors)

    def test_rejects_unsafe_url_scheme(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            (root / "src" / "App.jsx").write_text(APP + '\nconst bad = "javascript:alert(1)"', encoding="utf-8")
            report = validate_vite_project(root, "prototype")
            self.assertIn("unsafe_url_scheme: javascript", report.errors)

    def test_motion_requires_reduced_motion_rule(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            (root / "src" / "styles.css").write_text(":focus-visible { outline: 2px solid; }", encoding="utf-8")
            report = validate_vite_project(root, "motion")
            self.assertIn("missing_reduced_motion_rule", report.errors)

    def test_media_direction_requires_reduced_motion_rule(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            (root / "src" / "styles.css").write_text(":focus-visible { outline: 2px solid; }", encoding="utf-8")
            report = validate_vite_project(root, "media-direction")
            self.assertIn("missing_reduced_motion_rule", report.errors)

    def test_motion_enhanced_accepts_poster_only_media_component(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            (root / "src" / "App.jsx").write_text(APP + POSTER_MEDIA, encoding="utf-8")
            report = validate_vite_project(root, "motion-enhanced")
            self.assertTrue(report.ok, report.errors)

    def test_motion_enhanced_rejects_missing_poster_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            missing = "function Media(){return <div data-motion-media><video muted loop /></div>}"
            (root / "src" / "App.jsx").write_text(APP + missing, encoding="utf-8")
            report = validate_vite_project(root, "motion-enhanced")
            self.assertIn("missing_motion_poster", report.errors)

    def test_video_upgrade_requires_muted_loop_inline_and_poster(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            invalid = "function Media(){return <div data-motion-media><video src='/motion/a.mp4' /><img src='/motion/poster.webp' /></div>}"
            (root / "src" / "App.jsx").write_text(APP + invalid, encoding="utf-8")
            report = validate_vite_project(root, "video-upgrade")
            self.assertIn("invalid_video_embed_contract", report.errors)

    def test_video_upgrade_rejects_scroll_or_pointer_video_control(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_project(root)
            interactive = VIDEO_MEDIA + "\nvideo.currentTime = scrollY / 100;"
            (root / "src" / "App.jsx").write_text(APP + interactive, encoding="utf-8")
            report = validate_vite_project(root, "video-upgrade")
            self.assertIn("interactive_video_forbidden", report.errors)


if __name__ == "__main__":
    unittest.main()
