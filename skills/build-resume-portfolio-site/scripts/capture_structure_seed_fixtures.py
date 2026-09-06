from __future__ import annotations

import argparse
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright


SEEDS = ("split-narrative", "pinned-chapter-stage", "constellation-map")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def capture(dist: Path, output: Path) -> dict[str, object]:
    if not (dist / "index.html").is_file():
        raise ValueError(f"missing built fixture: {dist / 'index.html'}")
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(dist), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    output.mkdir(parents=True, exist_ok=True)
    evidence: list[dict[str, object]] = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                for seed in SEEDS:
                    for mode, viewport, reduced in (
                        ("desktop", {"width": 1440, "height": 1000}, "no-preference"),
                        ("mobile", {"width": 390, "height": 844}, "no-preference"),
                        ("reduced", {"width": 1440, "height": 1000}, "reduce"),
                    ):
                        page = browser.new_page(viewport=viewport, reduced_motion=reduced)
                        console_errors: list[str] = []
                        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
                        page.goto(f"http://127.0.0.1:{server.server_port}/?seed={seed}", wait_until="networkidle")
                        page.locator("main").screenshot(path=str(output / f"{seed}-{mode}.png"), animations="disabled")
                        metrics = page.evaluate("""() => ({
                          seed: document.querySelector('main')?.dataset.seed,
                          scrollWidth: document.documentElement.scrollWidth,
                          clientWidth: document.documentElement.clientWidth,
                          evidenceCount: document.querySelectorAll('.evidence').length,
                          visibleText: document.body.innerText.length
                        })""")
                        evidence.append({"requested_seed": seed, "mode": mode, "console_errors": console_errors, **metrics})
                        page.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
    report = {"ok": all(item["seed"] == item["requested_seed"] and item["scrollWidth"] <= item["clientWidth"] + 1 and item["evidenceCount"] == 4 and not item["console_errors"] for item in evidence), "evidence": evidence}
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture representative structure seed QA fixtures.")
    parser.add_argument("dist", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        report = capture(args.dist.resolve(), args.output.resolve())
    except Exception as error:
        print(f"ERROR: {error}")
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
