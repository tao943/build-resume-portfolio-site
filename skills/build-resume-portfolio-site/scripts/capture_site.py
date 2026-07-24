from __future__ import annotations

import argparse
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable, Sequence
from urllib.parse import quote


VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "tablet": {"width": 1024, "height": 768},
    "mobile": {"width": 390, "height": 844},
}

PLAYWRIGHT_INSTALL_COMMANDS = (
    "python -m pip install playwright",
    "python -m playwright install chromium",
)


class PlaywrightDependencyError(RuntimeError):
    def __init__(self, detail: str | None = None) -> None:
        guidance = "\n".join(PLAYWRIGHT_INSTALL_COMMANDS)
        message = "Playwright or Chromium is unavailable. Run:\n" + guidance
        if detail:
            message += f"\nDetail: {detail}"
        super().__init__(message)


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def _load_sync_playwright() -> Callable[[], object]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise PlaywrightDependencyError(str(error)) from error
    return sync_playwright


def prepare_capture_paths(html_path: Path, output_dir: Path) -> tuple[Path, Path]:
    html_path = html_path.resolve()
    if not html_path.is_file():
        raise FileNotFoundError(f"HTML file not found: {html_path}")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return html_path, output_dir


def _looks_like_missing_browser(error: Exception) -> bool:
    message = str(error).lower()
    return "executable doesn't exist" in message or "playwright install" in message


def capture_site(html_path: Path, output_dir: Path) -> dict[str, object]:
    html_path, output_dir = prepare_capture_paths(html_path, output_dir)
    sync_playwright = _load_sync_playwright()
    handler = partial(_QuietHandler, directory=str(html_path.parent))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    page_url = f"http://127.0.0.1:{server.server_port}/{quote(html_path.name)}"

    captures: list[dict[str, object]] = []
    console_errors: list[dict[str, str]] = []
    page_errors: list[dict[str, str]] = []
    try:
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch()
            except Exception as error:
                if _looks_like_missing_browser(error):
                    raise PlaywrightDependencyError(str(error)) from error
                raise
            try:
                for name, viewport in VIEWPORTS.items():
                    page = browser.new_page(viewport=viewport)

                    def on_console(message: object, viewport_name: str = name) -> None:
                        message_type = getattr(message, "type", "")
                        if callable(message_type):
                            message_type = message_type()
                        if message_type == "error":
                            text = getattr(message, "text", str(message))
                            if callable(text):
                                text = text()
                            console_errors.append({"viewport": viewport_name, "text": str(text)})

                    def on_page_error(error: object, viewport_name: str = name) -> None:
                        page_errors.append({"viewport": viewport_name, "text": str(error)})

                    page.on("console", on_console)
                    page.on("pageerror", on_page_error)
                    try:
                        page.goto(page_url, wait_until="networkidle", timeout=30_000)
                        screenshot_path = output_dir / f"{name}.png"
                        page.screenshot(path=str(screenshot_path), full_page=True)
                        captures.append(
                            {
                                "name": name,
                                "width": viewport["width"],
                                "height": viewport["height"],
                                "path": str(screenshot_path),
                            }
                        )
                    finally:
                        page.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)

    report: dict[str, object] = {
        "ok": len(captures) == len(VIEWPORTS),
        "html_path": str(html_path),
        "captures": captures,
        "console_errors": console_errors,
        "page_errors": page_errors,
    }
    (output_dir / "capture-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture a standalone site at three viewports.")
    parser.add_argument("html_path", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = capture_site(args.html_path, args.output_dir)
    except PlaywrightDependencyError as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False, indent=2))
        return 2
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
