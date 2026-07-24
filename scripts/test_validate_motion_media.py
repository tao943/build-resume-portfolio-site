from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_motion_media import POSTER_LIMIT, UPLOAD_VIDEO_LIMIT, validate_motion_media


def write_slot(root: Path) -> Path:
    path = root / "motion-media-slot.json"
    path.write_text(json.dumps({"resolved_placement": {"aspect_ratio": "16:9"}}), encoding="utf-8")
    return path


def valid_probe(*, duration: float = 6.0, audio: bool = False):
    def probe(_path: Path, _ffprobe: str) -> dict[str, object]:
        streams: list[dict[str, object]] = [{"codec_type": "video", "width": 1920, "height": 1080}]
        if audio:
            streams.append({"codec_type": "audio"})
        return {"format": {"duration": str(duration)}, "streams": streams}
    return probe


class MotionMediaTests(unittest.TestCase):
    def test_accepts_poster_only_as_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            poster = root / "poster.webp"
            poster.write_bytes(b"poster")
            report = validate_motion_media(poster, None, write_slot(root))
            self.assertTrue(report.ok, report.errors)
            self.assertTrue(report.ready)
            self.assertEqual(report.mode, "poster-only")

    def test_rejects_poster_larger_than_three_mib(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            poster = root / "poster.webp"
            poster.write_bytes(b"x" * (POSTER_LIMIT + 1))
            report = validate_motion_media(poster, None, write_slot(root))
            self.assertIn("poster_too_large", report.errors)

    def test_rejects_fake_mp4_extension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            poster = root / "poster.webp"; poster.write_bytes(b"poster")
            video = root / "clip.mp4"; video.write_bytes(b"not-an-mp4")
            report = validate_motion_media(poster, video, write_slot(root), probe=valid_probe())
            self.assertIn("invalid_video_container", report.errors)

    def test_rejects_video_longer_than_twelve_seconds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            poster = root / "poster.webp"; poster.write_bytes(b"poster")
            video = root / "clip.mp4"; video.write_bytes(b"\x00\x00\x00\x18ftypisom0000")
            report = validate_motion_media(poster, video, write_slot(root), probe=valid_probe(duration=12.1))
            self.assertIn("invalid_video_duration", report.errors)

    def test_rejects_uploaded_video_larger_than_fifty_mib(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            poster = root / "poster.webp"; poster.write_bytes(b"poster")
            video = root / "clip.webm"
            with video.open("wb") as handle:
                handle.write(b"\x1a\x45\xdf\xa3")
                handle.truncate(UPLOAD_VIDEO_LIMIT + 1)
            report = validate_motion_media(poster, video, write_slot(root), probe=valid_probe())
            self.assertIn("uploaded_video_too_large", report.errors)

    def test_reports_resource_blocked_when_ffprobe_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            poster = root / "poster.webp"; poster.write_bytes(b"poster")
            video = root / "clip.mp4"; video.write_bytes(b"\x00\x00\x00\x18ftypisom0000")
            def missing(_path: Path, _ffprobe: str) -> dict[str, object]:
                raise FileNotFoundError("ffprobe")
            report = validate_motion_media(poster, video, write_slot(root), probe=missing)
            self.assertTrue(report.ok)
            self.assertFalse(report.ready)
            self.assertIn("resource_blocked: ffprobe", report.errors)

    def test_warns_when_decorative_video_contains_audio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            poster = root / "poster.webp"; poster.write_bytes(b"poster")
            video = root / "clip.mp4"; video.write_bytes(b"\x00\x00\x00\x18ftypisom0000")
            report = validate_motion_media(poster, video, write_slot(root), probe=valid_probe(audio=True))
            self.assertIn("decorative_video_contains_audio", report.warnings)


if __name__ == "__main__":
    unittest.main()
