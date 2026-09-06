from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_design_contract.py"


def rule(rule_id: str, criterion: str, *evidence: str) -> dict:
    return {
        "rule_id": rule_id,
        "criterion": criterion,
        "evidence_required": list(evidence) or ["desktop-initial"],
        "severity": "repairable",
    }


def valid_report() -> dict:
    report = {
        "schema_version": 1,
        "identity_strategy": {
            "audience": "Product engineering teams hiring a creative technologist.",
            "narrative_priorities": [
                "Lead with shipped product evidence.",
                "Connect interaction craft to engineering decisions.",
            ],
            "density": "Editorially dense with deliberate breathing room.",
            "content_form_relationships": [
                "The primary project receives the dominant visual field.",
                "Supporting experience reads as an inspectable chronology.",
            ],
        },
        "signature": {
            "visual_protagonist": "An oversized project index anchors the page.",
            "composition_commitment": "Asymmetric editorial columns establish hierarchy.",
            "structural_device": "Project numbers bridge navigation and case-study rhythm.",
            "template_independence_claim": "Scale and numbering remain recognizable without media or motion.",
        },
        "layout": {
            "hierarchy": ["One dominant project before supporting evidence."],
            "section_rhythm": ["Alternate dense evidence with open transition fields."],
            "alignment_logic": "Use one editorial spine with intentional breakouts.",
            "density_ranges": ["Keep prose measures readable while allowing dense metadata."],
            "responsive_transformations": ["Stack breakouts into the editorial spine below tablet width."],
            "prohibited_arrangements": ["Do not flatten all projects into equal cards."],
        },
        "typography": {
            "roles": ["Expressive display", "neutral reading", "compact metadata"],
            "scale_relationships": ["Display type clearly dominates section headings."],
            "measure": ["Long-form copy stays within a comfortable reading measure."],
            "rhythm": ["Heading and body spacing follows a consistent vertical cadence."],
            "contrast": ["Metadata remains subordinate without becoming illegible."],
            "fallbacks": ["Fallback fonts preserve role contrast and line measure."],
        },
        "color": {
            "semantic_roles": ["Ink", "paper", "signal", "muted evidence"],
            "proportion_guidance": ["Signal color remains a controlled minority accent."],
            "contrast_targets": ["Text and interactive controls meet WCAG AA contrast."],
            "surface_relationships": ["Sections separate through tone before containers."],
            "prohibited_effects": ["Do not use glow as the default separator."],
        },
        "surface": {
            "container_rules": ["Use containers only when they clarify grouping."],
            "border_rules": ["Editorial rules reinforce the alignment spine."],
            "radius_rules": ["Radius expresses media framing, not every region."],
            "shadow_rules": ["Shadows indicate elevation only."],
            "texture_rules": ["Texture remains subtle and non-factual."],
            "repetition_rules": ["Avoid repeating one treatment across unrelated sections."],
        },
        "motion": {
            "primary_system": "Scroll-linked project index progression.",
            "secondary_effects": ["Directional link feedback"],
            "purposes": ["Reveal narrative priority and navigation state."],
            "controller_ownership": ["The page controller owns scroll progress."],
            "reduced_motion": ["Use static project index states in document order."],
            "coarse_pointer": ["Replace hover feedback with focus and tap states."],
            "fallbacks": ["All content remains visible when motion initialization fails."],
        },
        "anti_template_rules": [
            rule(
                "anti-template.uniform-card-repetition",
                "Unrelated content must not collapse into identical cards.",
                "desktop-initial",
                "mobile-initial",
            )
        ],
        "acceptance_checks": {
            "identity_fit": [
                rule("identity.project-priority", "The primary project visibly leads the narrative.")
            ],
            "aesthetic_quality": [
                rule("aesthetic.signature-visible", "The signature device survives without motion.")
            ],
            "accessibility": [
                rule("accessibility.focus-visible", "Interactive controls have visible focus.")
            ],
            "responsive": [
                rule("responsive.hierarchy-preserved", "Mobile preserves narrative priority.")
            ],
            "runtime_safety": [
                rule("runtime.no-console-errors", "The captured page has no console errors.")
            ],
        },
        "traceability": [],
    }
    report["traceability"] = [
        {
            "contract_path": section,
            "source_decision_ids": ["structure:editorial-index"],
            "creative_direction_paths": ["concept_prototype.composition_commitment"],
        }
        for section in (
            "identity_strategy",
            "signature",
            "layout",
            "typography",
            "color",
            "surface",
            "motion",
            "anti_template_rules",
            "acceptance_checks",
        )
    ]
    return report


def valid_v2_report() -> dict:
    report = valid_report()
    report["schema_version"] = 2
    report["structure"] = {
        "origin": "seed", "seed_id": "split-narrative",
        "topology": ["vertical axis", "sticky thesis lane", "split viewport"],
        "invariants": ["desktop lanes remain unequal"],
        "variation_choices": ["narrow thesis lane"],
        "responsive_transformations": ["linearize into marked chapters"],
        "anti_degeneracy_rules": ["do not collapse to uniform cards"],
        "compatible_motion_slots": ["evidence-progression"],
    }
    report["traceability"].append({
        "contract_path": "structure",
        "source_decision_ids": ["agent-selection:direction-fit"],
        "creative_direction_paths": ["structure_selection"],
    })
    return report


class DesignContractValidatorTests(unittest.TestCase):
    def run_validator(self, report: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "design-contract.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_complete_design_contract(self) -> None:
        result = self.run_validator(valid_report())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_accepts_v2_structure_contract(self) -> None:
        result = self.run_validator(valid_v2_report())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_v2_rejects_missing_seed_invariant(self) -> None:
        report = valid_v2_report()
        report["structure"]["invariants"] = []
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("structure.invariants", result.stdout)

    def test_accepts_no_secondary_effects(self) -> None:
        report = valid_report()
        report["motion"]["secondary_effects"] = []
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_schema_uses_exact_named_fields_for_design_system_sections(self) -> None:
        schema = json.loads(
            (SKILL_ROOT / "references" / "design-contract-schema.json").read_text(
                encoding="utf-8"
            )
        )
        expected = {
            "typography": {
                "roles", "scale_relationships", "measure", "rhythm", "contrast", "fallbacks"
            },
            "color": {
                "semantic_roles", "proportion_guidance", "contrast_targets",
                "surface_relationships", "prohibited_effects"
            },
            "surface": {
                "container_rules", "border_rules", "radius_rules", "shadow_rules",
                "texture_rules", "repetition_rules"
            },
        }
        for section, fields in expected.items():
            with self.subTest(section=section):
                definition = schema["properties"][section]
                self.assertFalse(definition["additionalProperties"])
                self.assertEqual(set(definition["required"]), fields)
                self.assertEqual(set(definition["properties"]), fields)

    def test_rejects_missing_signature(self) -> None:
        report = valid_report()
        del report["signature"]
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("signature", result.stdout)

    def test_rejects_duplicate_rule_ids(self) -> None:
        report = valid_report()
        report["acceptance_checks"]["identity_fit"][0]["rule_id"] = (
            report["anti_template_rules"][0]["rule_id"]
        )
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate rule_id", result.stdout)

    def test_rejects_missing_responsive_transformations(self) -> None:
        report = valid_report()
        report["layout"]["responsive_transformations"] = []
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("responsive_transformations", result.stdout)

    def test_rejects_missing_reduced_motion_or_coarse_pointer_fallback(self) -> None:
        for field in ("reduced_motion", "coarse_pointer", "fallbacks"):
            with self.subTest(field=field):
                report = valid_report()
                report["motion"][field] = []
                result = self.run_validator(report)
                self.assertEqual(result.returncode, 1)
                self.assertIn(field, result.stdout)

    def test_rejects_traceability_that_does_not_cover_each_design_section(self) -> None:
        report = valid_report()
        report["traceability"] = [
            item
            for item in report["traceability"]
            if item["contract_path"] != "signature"
        ]
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("traceability must cover signature", result.stdout)

    def test_rejects_unknown_traceability_contract_path(self) -> None:
        report = valid_report()
        report["traceability"][0]["contract_path"] = "components.hero"
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown contract_path", result.stdout)

    def test_rejects_implementation_payloads(self) -> None:
        report = valid_report()
        report["signature"]["component_tree"] = "<Hero />"
        result = self.run_validator(report)
        self.assertEqual(result.returncode, 1)
        self.assertIn("implementation payload", result.stdout)

    def test_cli_does_not_modify_invalid_input(self) -> None:
        report = valid_report()
        del report["signature"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "design-contract.json"
            path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            before = path.read_bytes()
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
