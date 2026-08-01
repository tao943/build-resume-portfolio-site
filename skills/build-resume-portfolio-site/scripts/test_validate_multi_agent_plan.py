from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_multi_agent_plan.py"


def valid_plan() -> dict:
    return {
        "schema_version": 1,
        "strategy": "parallel-wave",
        "integration_owner": "main-agent",
        "shared_files": ["src/App.jsx", "src/styles/global.css", "package.json"],
        "waves": [
            {"id": "wave-1", "mode": "parallel", "task_ids": ["hero", "gallery"]},
            {"id": "wave-2", "mode": "sequential", "task_ids": ["integration"]},
            {"id": "wave-3", "mode": "parallel", "task_ids": ["spec-review", "quality-review"]},
        ],
        "tasks": [
            {
                "id": "hero",
                "role": "implementation",
                "mode": "write",
                "depends_on": [],
                "allowed_files": ["src/components/Hero.jsx", "src/components/hero.css"],
                "acceptance": ["Hero media has a static fallback."],
                "verification": ["Run the Hero component test."],
            },
            {
                "id": "gallery",
                "role": "implementation",
                "mode": "write",
                "depends_on": [],
                "allowed_files": ["src/components/Gallery.jsx", "src/components/gallery.css"],
                "acceptance": ["Gallery works with keyboard input."],
                "verification": ["Run the Gallery component test."],
            },
            {
                "id": "integration",
                "role": "integration",
                "mode": "write",
                "depends_on": ["hero", "gallery"],
                "allowed_files": ["src/App.jsx", "src/styles/global.css", "package.json"],
                "acceptance": ["All approved sections are wired into the app."],
                "verification": ["Run npm run build."],
            },
            {
                "id": "spec-review",
                "role": "review",
                "mode": "read-only",
                "depends_on": ["integration"],
                "allowed_files": [],
                "acceptance": ["Check the implementation against the approved brief."],
                "verification": ["Report findings without editing files."],
            },
            {
                "id": "quality-review",
                "role": "audit",
                "mode": "read-only",
                "depends_on": ["integration"],
                "allowed_files": [],
                "acceptance": ["Check responsive, accessibility, and motion safety."],
                "verification": ["Report findings without editing files."],
            },
        ],
    }


class MultiAgentPlanValidatorTests(unittest.TestCase):
    def run_validator(self, plan: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "plan.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_a_valid_parallel_wave_plan(self) -> None:
        result = self.run_validator(valid_plan())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_parallel_file_overlap(self) -> None:
        plan = valid_plan()
        plan["tasks"][1]["allowed_files"].append("src/components/Hero.jsx")
        result = self.run_validator(plan)
        self.assertEqual(result.returncode, 1)
        self.assertIn("parallel file overlap", result.stdout)

    def test_rejects_shared_file_owned_by_non_integration_task(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["allowed_files"].append("src/App.jsx")
        result = self.run_validator(plan)
        self.assertEqual(result.returncode, 1)
        self.assertIn("shared file", result.stdout)

    def test_rejects_dependency_cycles(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["depends_on"] = ["integration"]
        result = self.run_validator(plan)
        self.assertEqual(result.returncode, 1)
        self.assertIn("dependency cycle", result.stdout)

    def test_rejects_a_writing_reviewer(self) -> None:
        plan = valid_plan()
        plan["tasks"][3]["mode"] = "write"
        result = self.run_validator(plan)
        self.assertEqual(result.returncode, 1)
        self.assertIn("must be read-only", result.stdout)

    def test_rejects_retired_fresh_agent_sequential_strategy(self) -> None:
        plan = valid_plan()
        plan["strategy"] = "fresh-agent-sequential"
        plan["waves"] = [
            {"id": "wave-1", "mode": "sequential", "task_ids": ["hero"]},
            {"id": "wave-2", "mode": "sequential", "task_ids": ["gallery"]},
            {
                "id": "wave-3",
                "mode": "sequential",
                "task_ids": ["integration"],
            },
            {
                "id": "wave-4",
                "mode": "sequential",
                "task_ids": ["spec-review"],
            },
            {
                "id": "wave-5",
                "mode": "sequential",
                "task_ids": ["quality-review"],
            },
        ]
        result = self.run_validator(plan)
        self.assertEqual(result.returncode, 1)
        self.assertIn("strategy must be parallel-wave", result.stdout)


if __name__ == "__main__":
    unittest.main()
