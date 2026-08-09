from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REQUIRED_MVP_FILES = (
    "README.md",
    "astron/workflow-spec.json",
    "astron/workflow-build-guide.md",
    "openapi/preview-plugin.openapi.yaml",
    "contracts/preview-request.example.json",
    "demo/anonymized-student-resume.md",
    "demo/target-jd.md",
    "demo/demo-script.md",
)
REQUIRED_SERVICE_FILES = (
    "package.json",
    "wrangler.toml.example",
    "src/validation.mjs",
    "src/worker.mjs",
    "test/validation.test.mjs",
    "test/worker.test.mjs",
)
SECRET_MARKERS = (
    "api_secret=",
    "preview_write_token=",
    "authorization: bearer sk-",
    "bearer sk-",
)


def _load_workflow_validator():
    path = Path(__file__).with_name("validate_workflow_spec.py")
    spec = importlib.util.spec_from_file_location("xinghuo_workflow_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load workflow validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate


def scan_for_secrets(root: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".mjs",
        }:
            continue
        text = path.read_text(encoding="utf-8").lower()
        if any(marker in text for marker in SECRET_MARKERS):
            errors.append(
                f"possible committed secret in {path.relative_to(root).as_posix()}"
            )
    return errors


def validate_release(root: Path) -> list[str]:
    root = root.resolve()
    errors = [
        f"missing release file: {relative}"
        for relative in REQUIRED_MVP_FILES
        if not (root / relative).is_file()
    ]

    prompts = sorted((root / "astron" / "prompts").glob("*.md"))
    if len(prompts) != 7:
        errors.append("release requires exactly seven node prompts")

    workflow_path = root / "astron" / "workflow-spec.json"
    if workflow_path.is_file():
        try:
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid workflow JSON: {exc}")
        else:
            errors.extend(_load_workflow_validator()(workflow))

    repo_root = root.parents[1]
    service_root = repo_root / "services" / "xinghuo-preview-worker"
    errors.extend(
        f"missing preview service file: {relative}"
        for relative in REQUIRED_SERVICE_FILES
        if not (service_root / relative).is_file()
    )
    errors.extend(scan_for_secrets(root))
    errors.extend(scan_for_secrets(service_root))
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_release.py <competition/xinghuo-cup-mvp>")
        return 2
    errors = validate_release(Path(sys.argv[1]))
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("OK: Xinghuo qualifier release bundle is complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
