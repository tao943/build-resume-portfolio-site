from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MVP = ROOT / "competition" / "xinghuo-cup-mvp"
VALIDATOR = MVP / "scripts" / "validate_workflow_spec.py"
RELEASE_VALIDATOR = MVP / "scripts" / "validate_release.py"


def valid_spec() -> dict:
    return {
        "schema_version": 1,
        "platform": "iflytek-astron-agent",
        "entry_kind": "workflow-agent",
        "approval_sources": ["explicit_conversation"],
        "state_variables": [
            "source_facts",
            "confirmed_facts",
            "clarification_queue",
            "jd_match_matrix",
            "approved_copy",
            "content_map",
            "creative_direction",
            "preview_artifact",
        ],
        "preview_service_capabilities": ["validate", "store", "serve"],
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "extract_facts", "type": "llm"},
            {"id": "validate_facts", "type": "code"},
            {"id": "clarification_decision", "type": "decision"},
            {"id": "clarification_question", "type": "question"},
            {"id": "jd_match", "type": "llm"},
            {"id": "content_strategies", "type": "llm"},
            {
                "id": "strategy_approval",
                "type": "question",
                "approval_kind": "content_strategy",
            },
            {"id": "tailored_copy", "type": "llm"},
            {
                "id": "copy_approval",
                "type": "question",
                "approval_kind": "final_copy",
            },
            {"id": "content_map", "type": "llm"},
            {"id": "creative_directions", "type": "llm"},
            {
                "id": "direction_approval",
                "type": "question",
                "approval_kind": "creative_direction",
            },
            {"id": "generate_preview_html", "type": "llm"},
            {"id": "preview_delivery", "type": "tool"},
            {"id": "preview_review", "type": "question"},
        ],
    }


def load_validate():
    if not VALIDATOR.is_file():
        raise AssertionError("workflow validator is missing")
    spec = importlib.util.spec_from_file_location("validate_workflow_spec", VALIDATOR)
    if spec is None or spec.loader is None:
        raise AssertionError("workflow validator cannot be imported")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate


def load_release_validator_module():
    if not RELEASE_VALIDATOR.is_file():
        raise AssertionError("release validator is missing")
    spec = importlib.util.spec_from_file_location("validate_release", RELEASE_VALIDATOR)
    if spec is None or spec.loader is None:
        raise AssertionError("release validator cannot be imported")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_validate_release():
    return load_release_validator_module().validate_release


class XinghuoWorkflowContractTests(unittest.TestCase):
    def test_valid_workflow_contract_is_accepted(self) -> None:
        self.assertEqual(load_validate()(valid_spec()), [])

    def test_browser_activity_cannot_be_an_approval_source(self) -> None:
        payload = valid_spec()
        payload["approval_sources"].append("browser_activity")
        self.assertIn(
            "approval_sources must equal ['explicit_conversation']",
            load_validate()(payload),
        )

    def test_preview_service_cannot_generate_content(self) -> None:
        payload = valid_spec()
        payload["preview_service_capabilities"].append("model_inference")
        self.assertIn(
            "preview service capability is forbidden: model_inference",
            load_validate()(payload),
        )

    def test_approval_gates_cannot_be_merged_or_reordered(self) -> None:
        payload = valid_spec()
        payload["nodes"] = [
            node for node in payload["nodes"] if node["id"] != "copy_approval"
        ]
        errors = load_validate()(payload)
        self.assertIn("workflow nodes are missing or out of order", errors)
        self.assertIn("approval gates must remain separate and ordered", errors)

    def test_persisted_workflow_and_fixture_match_the_contract(self) -> None:
        workflow_path = MVP / "astron" / "workflow-spec.json"
        fixture_path = ROOT / "tests" / "fixtures" / "xinghuo-workflow-valid.json"
        self.assertTrue(workflow_path.is_file(), "workflow spec is missing")
        self.assertTrue(fixture_path.is_file(), "workflow fixture is missing")
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertEqual(workflow, valid_spec())
        self.assertEqual(fixture, workflow)
        self.assertEqual(load_validate()(workflow), [])

    def test_prompt_pack_enforces_evidence_and_non_template_output(self) -> None:
        prompt_dir = MVP / "astron" / "prompts"
        prompts = sorted(prompt_dir.glob("*.md"))
        self.assertEqual(len(prompts), 7, "prompt pack must contain seven files")
        combined = "\n".join(path.read_text(encoding="utf-8") for path in prompts)
        for marker in (
            "FACT-",
            "EVID-",
            "unmatched",
            "user_confirmed",
            "approved_copy",
            "creative_direction",
            "No JavaScript",
            "Do not use a fixed portfolio template",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, combined)

    def test_build_guide_maps_every_workflow_node(self) -> None:
        workflow_path = MVP / "astron" / "workflow-spec.json"
        guide_path = MVP / "astron" / "workflow-build-guide.md"
        self.assertTrue(guide_path.is_file(), "workflow build guide is missing")
        spec = json.loads(workflow_path.read_text(encoding="utf-8"))
        guide = guide_path.read_text(encoding="utf-8")
        for node in spec["nodes"]:
            with self.subTest(node=node["id"]):
                self.assertIn(f"`{node['id']}`", guide)
        self.assertIn("平台导出的 YML", guide)
        self.assertIn("成功调试", guide)

    def test_openapi_matches_the_preview_worker_contract(self) -> None:
        contract_path = MVP / "openapi" / "preview-plugin.openapi.yaml"
        self.assertTrue(contract_path.is_file(), "preview OpenAPI contract is missing")
        contract = contract_path.read_text(encoding="utf-8")
        for marker in (
            "/api/v1/competition/previews:",
            "operationId: createPortfolioPreview",
            "bearerAuth",
            "approved_copy",
            "content_map",
            "creative_direction",
            "generated_html",
            "preview_url",
            "validation_failed",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)

    def test_release_bundle_is_complete(self) -> None:
        self.assertEqual(load_validate_release()(MVP), [])

    def test_release_validator_detects_committed_secrets(self) -> None:
        module = load_release_validator_module()
        self.assertTrue(
            hasattr(module, "scan_for_secrets"),
            "release secret scanner is missing",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unsafe.md").write_text(
                "PREVIEW_WRITE_TOKEN=real-secret-value",
                encoding="utf-8",
            )
            self.assertEqual(
                module.scan_for_secrets(root),
                ["possible committed secret in unsafe.md"],
            )

    def test_demo_fixture_contains_no_real_contact_details(self) -> None:
        demo_path = MVP / "demo" / "anonymized-student-resume.md"
        self.assertTrue(demo_path.is_file(), "anonymized resume fixture is missing")
        demo = demo_path.read_text(encoding="utf-8")
        self.assertNotRegex(demo, r"1[3-9]\d{9}")
        self.assertNotRegex(
            demo,
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        )
        self.assertIn("候选人 A", demo)
        self.assertIn("示例大学", demo)

    def test_demo_script_exercises_all_approval_and_delivery_gates(self) -> None:
        script_path = MVP / "demo" / "demo-script.md"
        self.assertTrue(script_path.is_file(), "demo script is missing")
        script = script_path.read_text(encoding="utf-8")
        for marker in (
            "内容策略批准",
            "最终文案批准",
            "创意方向批准",
            "在线预览",
            "unmatched",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, script)


if __name__ == "__main__":
    unittest.main()
