from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence


POSTER_LIMIT = 3 * 1024 * 1024
UPLOAD_VIDEO_LIMIT = 50 * 1024 * 1024
DESKTOP_VIDEO_LIMIT = 15 * 1024 * 1024
MOBILE_VIDEO_LIMIT = 8 * 1024 * 1024
MIN_DURATION = 4.0
MAX_DURATION = 12.0


@dataclass(frozen=True)
class MediaReport:
    ok: bool
    ready: bool
    mode: str
    container: str | None
    duration: float | None
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def detect_video_container(header: bytes) -> str | None:
    if len(header) >= 12 and header[4:8] == b"ftyp":
        return "mp4"
    if header.startswith(b"\x1a\x45\xdf\xa3"):
        return "webm"
    return None


def _probe_video(path: Path, ffprobe: str) -> dict[str, object]:
    command = [
        ffprobe, "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_type,width,height",
        "-of", "json", str(path),
    ]
    completed = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", check=False
    )
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or "ffprobe_failed")
    data = json.loads(completed.stdout)
    if not isinstance(data, dict):
        raise ValueError("ffprobe_root_must_be_object")
    return data


def validate_motion_media(
    poster_path: Path,
    video_path: Path | None,
    slot_path: Path,
    ffprobe: str = "ffprobe",
    probe: Callable[[Path, str], dict[str, object]] = _probe_video,
) -> MediaReport:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        slot = json.loads(slot_path.read_text(encoding="utf-8"))
        if not isinstance(slot, dict) or not isinstance(slot.get("resolved_placement"), dict):
            errors.append("invalid_media_slot")
    except (OSError, UnicodeError, json.JSONDecodeError):
        errors.append("invalid_media_slot")

    if not poster_path.is_file():
        errors.append("missing_poster")
    elif poster_path.stat().st_size > POSTER_LIMIT:
        errors.append("poster_too_large")
    if errors or video_path is None:
        return MediaReport(not errors, not errors, "poster-only", None, None, tuple(errors), tuple(warnings))

    if not video_path.is_file():
        return MediaReport(False, False, "video", None, None, ("missing_video",), ())
    size = video_path.stat().st_size
    if size > UPLOAD_VIDEO_LIMIT:
        errors.append("uploaded_video_too_large")
    if size > DESKTOP_VIDEO_LIMIT:
        warnings.append("desktop_video_budget_exceeded")
    if size > MOBILE_VIDEO_LIMIT:
        warnings.append("mobile_video_budget_exceeded")
    with video_path.open("rb") as handle:
        container = detect_video_container(handle.read(32))
    if container is None or video_path.suffix.lower() != f".{container}":
        errors.append("invalid_video_container")
    if errors:
        return MediaReport(False, False, "video", container, None, tuple(errors), tuple(warnings))

    try:
        metadata = probe(video_path, ffprobe)
    except FileNotFoundError:
        return MediaReport(True, False, "video", container, None, ("resource_blocked: ffprobe",), tuple(warnings))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return MediaReport(False, False, "video", container, None, (f"invalid_video_metadata: {error}",), tuple(warnings))

    try:
        format_data = metadata.get("format", {})
        duration = float(format_data.get("duration")) if isinstance(format_data, dict) else 0.0
    except (TypeError, ValueError):
        duration = 0.0
    if not MIN_DURATION <= duration <= MAX_DURATION:
        errors.append("invalid_video_duration")
    streams = metadata.get("streams")
    if not isinstance(streams, list) or not any(
        isinstance(stream, dict) and stream.get("codec_type") == "video" for stream in streams
    ):
        errors.append("missing_video_stream")
    if isinstance(streams, list) and any(
        isinstance(stream, dict) and stream.get("codec_type") == "audio" for stream in streams
    ):
        warnings.append("decorative_video_contains_audio")
    return MediaReport(not errors, not errors, "video", container, duration, tuple(errors), tuple(warnings))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Poster and optional local motion video")
    parser.add_argument("--poster", type=Path, required=True)
    parser.add_argument("--video", type=Path)
    parser.add_argument("--slot", type=Path, required=True)
    parser.add_argument("--ffprobe", default="ffprobe")
    args = parser.parse_args(argv)
    report = validate_motion_media(args.poster, args.video, args.slot, ffprobe=args.ffprobe)
    print(json.dumps(asdict(report), ensure_ascii=False))
    return 0 if report.ok and report.ready else (2 if report.ok else 1)


if __name__ == "__main__":
    raise SystemExit(main())
