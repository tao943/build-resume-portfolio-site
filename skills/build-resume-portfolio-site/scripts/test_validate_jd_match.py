from __future__ import annotations

import unittest

from validate_jd_match import validate


def valid_report() -> dict:
    return {
        "schema_version": 1,
        "jd_source": {
            "source_id": "source-jd",
            "path": "inputs/job-description.txt",
            "sha256": "a" * 64,
        },
        "target_role": "Frontend Engineer",
        "organization": "Example Company",
        "requirements": [
            {
                "id": "jd-react",
                "category": "core_capability",
                "exact_phrase": "Build production React applications",
                "normalized_concept": "React production development",
                "priority": "high",
            },
            {
                "id": "jd-graphql",
                "category": "bonus_signal",
                "exact_phrase": "GraphQL experience preferred",
                "normalized_concept": "GraphQL",
                "priority": "medium",
            },
        ],
        "matches": [
            {
                "jd_item_id": "jd-react",
                "fact_ids": ["fact-project-react"],
                "evidence_ids": ["evidence-resume-12"],
                "status": "strong_match",
                "resume_location": "projects.portfolio",
                "rationale": "The project evidence names React and a production deployment.",
            },
            {
                "jd_item_id": "jd-graphql",
                "fact_ids": [],
                "evidence_ids": [],
                "status": "unmatched",
                "resume_location": "not present",
                "rationale": "No supplied source mentions GraphQL.",
            },
        ],
        "unmatched_requirement_ids": ["jd-graphql"],
        "clarification_candidates": ["Ask whether the user has unlisted GraphQL evidence."],
        "role_specific_copy_layer_id": "frontend-engineer-v1",
    }


class JdMatchValidatorTests(unittest.TestCase):
    def test_accepts_evidence_linked_report(self) -> None:
        self.assertEqual(validate(valid_report()), [])

    def test_rejects_matched_row_without_fact_and_evidence(self) -> None:
        report = valid_report()
        report["matches"][0]["fact_ids"] = []
        report["matches"][0]["evidence_ids"] = []
        errors = validate(report)
        self.assertIn("jd-react matched rows require fact_ids and evidence_ids", errors)

    def test_rejects_unmatched_row_with_invented_evidence(self) -> None:
        report = valid_report()
        report["matches"][1]["fact_ids"] = ["fact-invented"]
        report["matches"][1]["evidence_ids"] = ["evidence-invented"]
        errors = validate(report)
        self.assertIn("jd-graphql unmatched rows cannot cite facts or evidence", errors)

    def test_rejects_inconsistent_unmatched_requirement_ids(self) -> None:
        report = valid_report()
        report["unmatched_requirement_ids"] = []
        errors = validate(report)
        self.assertIn("unmatched_requirement_ids must equal unmatched match rows", errors)

    def test_rejects_unknown_category_and_status(self) -> None:
        report = valid_report()
        report["requirements"][0]["category"] = "nice_to_have"
        report["matches"][0]["status"] = "excellent"
        errors = validate(report)
        self.assertIn("jd-react has invalid category", errors)
        self.assertIn("jd-react has invalid match status", errors)


if __name__ == "__main__":
    unittest.main()
