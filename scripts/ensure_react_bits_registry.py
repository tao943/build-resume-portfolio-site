from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


REGISTRY_URL = "https://reactbits.dev/r/{name}.json"


@dataclass(frozen=True)
class RegistryResult:
    changed: bool
    path: str
    tsx: bool
    registry: str


def _detect_tsx(project_dir: Path) -> bool:
    source_dir = project_dir / "src"
    return any(path.suffix.lower() in {".ts", ".tsx"} for path in source_dir.rglob("*"))


def _default_config(tsx: bool) -> dict[str, object]:
    return {
        "$schema": "https://ui.shadcn.com/schema.json",
        "style": "new-york",
        "rsc": False,
        "tsx": tsx,
        "tailwind": {
            "config": "",
            "css": "src/index.css",
            "baseColor": "neutral",
            "cssVariables": True,
            "prefix": "",
        },
        "iconLibrary": "lucide",
        "aliases": {
            "components": "@/components",
            "utils": "@/lib/utils",
            "ui": "@/components/ui",
            "lib": "@/lib",
            "hooks": "@/hooks",
        },
        "registries": {},
    }


def _write_json_atomic(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary_name, path)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def ensure_registry(project_dir: Path) -> RegistryResult:
    project_dir = project_dir.resolve()
    if not (project_dir / "src").is_dir():
        raise ValueError(f"missing Vite src directory: {project_dir / 'src'}")

    path = project_dir / "components.json"
    tsx = _detect_tsx(project_dir)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(f"invalid components.json: {error}") from error
        if not isinstance(data, dict):
            raise ValueError("invalid components.json: root must be an object")
    else:
        data = _default_config(tsx)

    registries = data.get("registries")
    if registries is None:
        registries = {}
        data["registries"] = registries
    if not isinstance(registries, dict):
        raise ValueError("invalid components.json: registries must be an object")

    changed = registries.get("@react-bits") != REGISTRY_URL
    if not path.exists():
        changed = True
    registries["@react-bits"] = REGISTRY_URL
    if changed:
        _write_json_atomic(path, data)

    return RegistryResult(changed, str(path), bool(data.get("tsx", tsx)), REGISTRY_URL)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create or update components.json with the official React Bits registry."
    )
    parser.add_argument("project_dir", type=Path)
    args = parser.parse_args(argv)
    try:
        result = ensure_registry(args.project_dir)
    except ValueError as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, **asdict(result)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
