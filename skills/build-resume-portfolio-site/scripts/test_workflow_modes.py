from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_validate_site_design_spec import valid_spec_v4
from validate_site_design_spec import validate as validate_spec
from validate_site_implementation_plan import validate as validate_plan

TODO = b"- Build the approved portfolio in site/src/App.jsx and verify its mobile layout.\n"


def quick_spec():
    spec = valid_spec_v4()
    spec["interaction_mode"] = "quick"
    selections = {}
    for category, decision in spec["decisions"].items():
        decision["approval"]["bundle_id"] = "bundle-1"
        if category != "structure":
            selections[category] = decision.get("selected_candidate_ids", [])
        if "preview" in decision:
            decision["preview"]["artifact"] = ".resume-site-work/style-preview/sessions/shared/gallery.html"
    spec["requirements_approval"]["bundle_id"] = "bundle-1"
    spec["bundle_approval"] = {
        "id": "bundle-1", "quote": "Approve this design and plan; choose the execution approach.",
        "status": "user_approved", "source": "explicit_user", "channel": "conversation",
        "structure_delegated": True, "execution_delegated": True,
        "todo_plan": ".resume-site-work/reports/site-todo-plan.md",
        "todo_plan_sha256": hashlib.sha256(TODO).hexdigest(),
        "selected_candidate_ids": copy.deepcopy(selections),
    }
    return spec


def quick_plan():
    return {
        "schema_version": 2, "interaction_mode": "quick", "bundle_approval_id": "bundle-1",
        "design_spec_id": "site-spec-1", "todo_plan": ".resume-site-work/reports/site-todo-plan.md",
        "todo_plan_approval": {"status": "user_approved", "source": "explicit_user", "channel": "conversation", "bundle_id": "bundle-1"},
        "generation_mode": "one-integrated-site", "strategy": "single-agent",
        "strategy_selection": {"status": "agent_selected", "source": "approved_bundle", "channel": "workflow", "bundle_id": "bundle-1", "selected": "single-agent", "recommended": "single-agent", "reasons": ["One shared component tree."]},
        "multi_agent_authorized": False, "multi_agent_plan": None,
        "rollback_baseline": "new-project", "snapshot_target": "versions/v1-integrated",
        "tasks": [{"id": "site", "depends_on": [], "files": ["site/src/App.jsx"], "consumes": ["approved-copy.json"], "produces": ["portfolio"], "acceptance": ["Mobile readable"], "verification": ["Build and inspect"]}],
    }


class WorkflowModeTests(unittest.TestCase):
    def test_quick_bundle_and_delegated_execution_validate(self):
        self.assertEqual(validate_spec(quick_spec()), [])
        self.assertEqual(validate_plan(quick_plan(), quick_spec(), TODO), [])

    def test_existing_deep_spec_and_explicit_strategy_remain_valid(self):
        self.assertEqual(validate_spec(valid_spec_v4()), [])
        plan = quick_plan()
        plan.pop("interaction_mode")
        plan.pop("bundle_approval_id")
        plan["strategy_selection"].update(status="user_selected", source="explicit_user", channel="conversation")
        self.assertEqual(validate_plan(plan), [])

    def test_mode_selection_cannot_replace_bundle_approval(self):
        spec = quick_spec()
        spec.pop("bundle_approval")
        self.assertTrue(validate_spec(spec))
        spec = quick_spec()
        spec["bundle_approval"]["quote"] = ""
        self.assertTrue(validate_spec(spec))

    def test_changed_selection_or_browser_approval_is_rejected(self):
        spec = quick_spec()
        spec["decisions"]["color"]["selected_candidate_ids"] = ["color-2"]
        self.assertIn("color selection differs from the approved bundle", validate_spec(spec))
        spec = quick_spec()
        spec["bundle_approval"]["channel"] = "browser"
        self.assertTrue(validate_spec(spec))

    def test_quick_reuses_one_gallery(self):
        spec = quick_spec()
        spec["decisions"]["color"]["preview"]["artifact"] = ".resume-site-work/style-preview/sessions/another/gallery.html"
        self.assertIn("quick mode must reuse one preview gallery", validate_spec(spec))

    def test_changed_plan_or_missing_artifacts_are_rejected(self):
        self.assertIn("TODO plan changed after bundle approval", validate_plan(quick_plan(), quick_spec(), TODO + b"extra scope"))
        self.assertTrue(validate_plan(quick_plan()))
        plan = quick_plan()
        plan["bundle_approval_id"] = "old-bundle"
        self.assertTrue(validate_plan(plan, quick_spec(), TODO))

    def test_deep_mode_cannot_use_agent_selection_without_delegation(self):
        plan = quick_plan()
        plan["interaction_mode"] = "deep"
        self.assertIn("strategy selection must be explicit and conversational", validate_plan(plan))

    def test_parallel_mode_still_requires_authorization_and_plan(self):
        plan = quick_plan()
        plan["strategy"] = "parallel-wave"
        plan["strategy_selection"].update(selected="parallel-wave", recommended="parallel-wave")
        errors = validate_plan(plan, quick_spec(), TODO)
        self.assertIn("multi-agent strategy requires explicit authorization", errors)
        self.assertIn("multi-agent strategy requires a validated plan", errors)

    def test_quick_plan_cli_checks_real_todo_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reports = root / ".resume-site-work/reports"
            reports.mkdir(parents=True)
            todo = reports / "site-todo-plan.md"
            todo.write_bytes(TODO)
            spec = reports / "site-design-spec.json"
            spec.write_text(json.dumps(quick_spec()), encoding="utf-8")
            plan = reports / "site-implementation-plan.json"
            plan.write_text(json.dumps(quick_plan()), encoding="utf-8")
            command = [sys.executable, str(Path(__file__).with_name("validate_site_implementation_plan.py")), str(plan), "--design-spec", str(spec), "--workspace-root", str(root)]
            passed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(passed.returncode, 0, passed.stdout)
            todo.write_bytes(TODO + b"Changed scope")
            rejected = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 1)
            self.assertIn("changed after bundle approval", rejected.stdout)


if __name__ == "__main__":
    unittest.main()
