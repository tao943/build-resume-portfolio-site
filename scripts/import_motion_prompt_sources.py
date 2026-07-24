from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


SOURCE_IDS = (
    "01-minimalist-3d-ribbon",
    "02-dark-portfolio-stack",
    "03-cinematic-travel",
    "04-editorial-healthcare",
    "05-outdoor-video-mask",
    "06-creator-portfolio",
    "07-vex-video-hero",
    "08-securify-typography",
    "09-neural-kinetics",
    "10-biotech-video",
    "11-assist-floating-cards",
)

BLOCK_START = re.compile(r"(?m)^(\d+)、")
TRAILER_MARKER = "\n---\n\n"


@dataclass(frozen=True)
class PromptSource:
    source_id: str
    original_number: int
    body: str


def split_prompt_sources(
    text: str, *, source_ids: Sequence[str] = SOURCE_IDS
) -> list[PromptSource]:
    matches = list(BLOCK_START.finditer(text))
    if len(matches) != len(source_ids):
        raise ValueError(
            f"expected {len(source_ids)} numbered prompt blocks, found {len(matches)}"
        )

    sources: list[PromptSource] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.start() : end].strip()
        if index == len(matches) - 1 and TRAILER_MARKER in body:
            body = body.rsplit(TRAILER_MARKER, 1)[0].rstrip()
        sources.append(
            PromptSource(
                source_id=source_ids[index],
                original_number=int(match.group(1)),
                body=body,
            )
        )
    return sources


def write_prompt_sources(
    sources: Sequence[PromptSource], output_dir: Path
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for source in sources:
        path = output_dir / f"{source.source_id}.md"
        content = (
            "---\n"
            f"source_id: {source.source_id}\n"
            f"original_number: {source.original_number}\n"
            "usage_scope: motion-recipe-source-only\n"
            "---\n\n"
            f"{source.body}\n"
        )
        path.write_text(content, encoding="utf-8", newline="\n")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Preserve motion prompt source blocks")
    parser.add_argument("source", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    sources = split_prompt_sources(args.source.read_text(encoding="utf-8"))
    written = write_prompt_sources(sources, args.output_dir)
    print(f"wrote {len(written)} motion prompt sources to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
