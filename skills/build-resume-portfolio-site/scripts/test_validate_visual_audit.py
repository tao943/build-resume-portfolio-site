from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_validate_design_contract import valid_report as valid_design_contract, valid_v2_report as valid_v2_design_contract


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_visual_audit.py"


def capture(capture_id: str, viewport: str, state: str = "initial") -> dict:
    return {
        "id": capture_id,
        "viewport": viewport,
        "state": state,
        "path": f"captures/{capture_id}.png",
    }


def valid_audit() -> dict:
    return {
        "schema_version": 1,
        "candidate_id": "v1-integrated",
        "design_contract": "reports/design-contract.json",
        "repair_round": 0,
        "captures": [
            capture("desktop-initial", "desktop"),
            capture("tablet-initial", "tablet"),
            capture("mobile-initial", "mobile"),
        ],
        "deterministic_checks": [
            {
                "rule_id": "runtime.no-console-errors",
                "status": "pass",
                "evidence_refs": ["desktop-initial", "mobile-initial"],
                "contract_path": "acceptance_checks.runtime_safety",
                "note": "Capture report contains no page or console errors.",
            }
        ],
        "dimension_reviews": {
            "identity_fit": {
                "status": "pass",
                "verdict": "The narrative is specific to the approved portfolio.",
                "strengths": ["The primary project clearly leads."],
                "evidence_refs": ["desktop-initial", "mobile-initial"],
                "contract_paths": ["identity_strategy", "signature"],
            },
            "aesthetic_quality": {
                "status": "repairable",
                "verdict": "The signature works; mobile rhythm needs a bounded repair.",
                "strengths": ["The project index remains recognizable."],
                "evidence_refs": ["desktop-initial", "tablet-initial", "mobile-initial"],
                "contract_paths": ["signature", "layout", "typography"],
            },
        },
        "findings": [
            {
                "id": "finding-001",
                "rule_id": "aesthetic.signature-visible",
                "dimension": "aesthetic_quality",
                "severity": "repairable",
                "viewport_or_state": "mobile-initial",
                "region": "projects",
                "evidence_refs": ["mobile-initial"],
                "contract_path": "signature.structural_device",
                "permitted_files": [
                    "src/components/ProjectsSection.jsx",
                    "src/styles/projects.css",
                ],
                "proposed_local_change": "Restore project-number prominence on mobile.",
                "intended_result": "The signature project index remains immediately visible.",
            }
        ],
        "interaction_states_checked": [
            {
                "controller_family": "scroll",
                "target": "project-index",
                "trigger": "document scroll",
                "capture_refs": ["desktop-initial"],
                "coarse_pointer": "static ordered index",
                "reduced_motion": "static ordered index",
                "status": "pass",
            }
        ],
        "overall_status": "repairable",
    }


def valid_v2_audit() -> dict:
    audit = valid_audit()
    audit["schema_version"] = 2
    audit["structure_review"] = {
        "seed_identity": "pass", "visual_protagonist": "pass",
        "mobile_transformation": "pass", "static_without_motion": "pass",
        "novelty_not_palette_only": "pass",
        "evidence_refs": ["desktop-initial", "mobile-initial"],
        "contract_paths": ["structure", "signature"],
    }
    return audit


class VisualAuditValidatorTests(unittest.TestCase):
    def run_validator(
        self, audit: dict, contract: dict | None = None
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audit_path = root / "visual-audit.json"
            contract_path = root / "design-contract.json"
            audit_path.write_text(json.dumps(audit), encoding="utf-8")
            contract_path.write_text(
                json.dumps(contract or valid_design_contract()), encoding="utf-8"
            )
            return subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(audit_path),
                    "--design-contract",
                    str(contract_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_contract_linked_visual_audit(self) -> None:
        result = self.run_validator(valid_audit())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_accepts_v2_structure_review(self) -> None:
        result = self.run_validator(valid_v2_audit(), valid_v2_design_contract())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_v2_rejects_motion_dependent_static_composition(self) -> None:
        audit = valid_v2_audit()
        audit["structure_review"]["static_without_motion"] = "blocking"
        audit["overall_status"] = "blocking"
        result = self.run_validator(audit, valid_v2_design_contract())
        self.assertEqual(result.returncode, 1)
        self.assertIn("structure review must pass", result.stdout)

    def test_rejects_unknown_evidence_reference(self) -> None:
        audit = valid_audit()
        audit["findings"][0]["evidence_refs"] = ["missing-capture"]
        result = self.run_validator(audit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown evidence reference", result.stdout)

    def test_rejects_unknown_rule_id(self) -> None:
        audit = valid_audit()
        audit["findings"][0]["rule_id"] = "aesthetic.unknown"
        result = self.run_validator(audit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown rule_id", result.stdout)

    def test_rejects_unknown_contract_path(self) -> None:
        audit = valid_audit()
        audit["findings"][0]["contract_path"] = "components.hero"
        result = self.run_validator(audit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown contract_path", result.stdout)

    def test_rejects_missing_identity_or_aesthetic_dimension(self) -> None:
        for dimension in ("identity_fit", "aesthetic_quality"):
            with self.subTest(dimension=dimension):
                audit = valid_audit()
                del audit["dimension_reviews"][dimension]
                result = self.run_validator(audit)
                self.assertEqual(result.returncode, 1)
                self.assertIn("dimension_reviews", result.stdout)

    def test_rejects_understated_overall_status(self) -> None:
        audit = valid_audit()
        audit["findings"][0]["severity"] = "blocking"
        audit["overall_status"] = "repairable"
        result = self.run_validator(audit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("overall_status understates", result.stdout)

    def test_rejects_repair_round_greater_than_two(self) -> None:
        audit = valid_audit()
        audit["repair_round"] = 3
        result = self.run_validator(audit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("repair_round", result.stdout)

    def test_rejects_finding_without_repair_boundaries(self) -> None:
        for field in ("permitted_files", "intended_result"):
            with self.subTest(field=field):
                audit = valid_audit()
                del audit["findings"][0][field]
                result = self.run_validator(audit)
                self.assertEqual(result.returncode, 1)
                self.assertIn(field, result.stdout)

    def test_rejects_missing_required_viewport_capture(self) -> None:
        audit = valid_audit()
        audit["captures"] = [
            item for item in audit["captures"] if item["viewport"] != "tablet"
        ]
        result = self.run_validator(audit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("tablet", result.stdout)


if __name__ == "__main__":
    unittest.main()
