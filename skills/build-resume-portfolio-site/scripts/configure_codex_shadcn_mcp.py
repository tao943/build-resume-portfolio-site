from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


SHADCN_BLOCK = """[mcp_servers.shadcn]
command = "npx"
args = ["shadcn@latest", "mcp"]
"""


@dataclass(frozen=True)
class McpConfigResult:
    changed: bool
    path: str


def _replace_shadcn_block(text: str) -> str:
    pattern = re.compile(
        r"(?ms)^\[mcp_servers\.shadcn\][ \t]*\r?\n.*?(?=^\[|\Z)"
    )
    if pattern.search(text):
        updated = pattern.sub(SHADCN_BLOCK + "\n", text, count=1)
    else:
        prefix = text.rstrip()
        updated = f"{prefix}\n\n{SHADCN_BLOCK}" if prefix else SHADCN_BLOCK
    return updated.rstrip() + "\n"


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        os.replace(temporary_name, path)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def ensure_shadcn_mcp(config_path: Path) -> McpConfigResult:
    config_path = config_path.resolve()
    current = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    updated = _replace_shadcn_block(current)
    changed = updated != current
    if changed:
        _write_atomic(config_path, updated)
    return McpConfigResult(changed, str(config_path))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Idempotently enable the official shadcn MCP server in Codex."
    )
    parser.add_argument("config_path", type=Path)
    args = parser.parse_args(argv)
    result = ensure_shadcn_mcp(args.config_path)
    print(json.dumps({"ok": True, **asdict(result)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
