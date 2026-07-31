from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_site_design_spec.py"


def _candidates(prefix: str, count: int = 2) -> list[dict[str, object]]:
    return [
        {
            "id": f"{prefix}-{index}",
            "label": f"{prefix.title()} {index}",
            "tradeoffs": [f"{prefix} tradeoff {index}"],
        }
        for index in range(1, count + 1)
    ]


def confirmed_decision(
    category: str,
    *,
    selected: list[str] | None = None,
    response: str = "accepted",
) -> dict[str, object]:
    candidates = _candidates(category, 3 if category == "secondary-motion" else 2)
    selected_ids = selected or [str(candidates[0]["id"])]
    preview = {
        "offered": True,
        "response": response,
        "delivery": "local-gallery" if response == "accepted" else "not-requested",
        "artifact": (
            f".resume-site-work/style-preview/sessions/{category}-1/gallery.html"
            if response == "accepted"
            else None
        ),
    }
    return {
        "status": "confirmed",
        "candidates": candidates,
        "recommended_candidate_id": candidates[0]["id"],
        "tentative_selection_ids": [candidates[0]["id"]],
        "selected_candidate_ids": selected_ids,
        "preview": preview,
        "approval": {
            "status": "user_approved",
            "source": "explicit_user",
            "channel": "conversation",
        },
    }


def valid_spec() -> dict[str, object]:
    secondary = confirmed_decision("secondary-motion")
    secondary["selected_candidate_ids"] = [
        secondary["candidates"][0]["id"],
        secondary["candidates"][1]["id"],
    ]
    return {
        "schema_version": 3,
        "spec_id": "site-spec-1",
        "workflow_mode": "full",
        "content_revision": 1,
        "decision_order": [
            "structure",
            "typography",
            "color",
            "media",
            "primary_motion",
            "secondary_motion",
        ],
        "decisions": {
            "structure": confirmed_decision("structure"),
            "typography": confirmed_decision("typography"),
            "color": confirmed_decision("color"),
            "media": {
                "status": "skipped",
                "skip_reason": "no authorized media",
            },
            "primary_motion": confirmed_decision("primary-motion"),
            "secondary_motion": secondary,
        },
        "engineering_constraints": [
            "responsive",
            "accessible",
            "coarse-pointer",
            "reduced-motion",
            "media-fallbacks",
        ],
        "requirements_approval": {
            "status": "user_approved",
            "source": "explicit_user",
            "channel": "conversation",
        },
    }


class SiteDesignSpecValidatorTests(unittest.TestCase):
    def run_validator(self, payload: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spec.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_valid_full_spec(self) -> None:
        self.assertEqual(self.run_validator(valid_spec()).returncode, 0)

    def test_rejects_wrong_decision_order(self) -> None:
        payload = valid_spec()
        payload["decision_order"][0:2] = ["typography", "structure"]
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("decision_order", result.stdout)

    def test_rejects_missing_preview_offer_for_enabled_category(self) -> None:
        payload = valid_spec()
        payload["decisions"]["color"]["preview"]["offered"] = False
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("color preview must be offered", result.stdout)

    def test_accepts_declined_preview_and_later_accepted_preview(self) -> None:
        payload = valid_spec()
        payload["decisions"]["structure"]["preview"] = {
            "offered": True,
            "response": "declined",
            "delivery": "not-requested",
            "artifact": None,
        }
        self.assertEqual(self.run_validator(payload).returncode, 0)
        self.assertEqual(
            payload["decisions"]["typography"]["preview"]["response"],
            "accepted",
        )

    def test_rejects_media_skip_without_reason(self) -> None:
        payload = valid_spec()
        payload["decisions"]["media"].pop("skip_reason")
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("media skip requires a reason", result.stdout)

    def test_rejects_multiple_primary_motion_selections(self) -> None:
        payload = valid_spec()
        decision = payload["decisions"]["primary_motion"]
        decision["selected_candidate_ids"] = [
            decision["candidates"][0]["id"],
            decision["candidates"][1]["id"],
        ]
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "primary_motion requires exactly one selected candidate",
            result.stdout,
        )

    def test_accepts_multiple_compatible_secondary_motion_selections(self) -> None:
        payload = valid_spec()
        decision = payload["decisions"]["secondary_motion"]
        decision["selected_candidate_ids"] = [
            candidate["id"] for candidate in decision["candidates"]
        ]
        self.assertEqual(self.run_validator(payload).returncode, 0)

    def test_rejects_unknown_secondary_motion_selection(self) -> None:
        payload = valid_spec()
        payload["decisions"]["secondary_motion"][
            "selected_candidate_ids"
        ] = ["unknown-effect"]
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_unapproved_final_requirements(self) -> None:
        payload = valid_spec()
        payload["requirements_approval"]["status"] = "pending"
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("final requirements require user approval", result.stdout)

    def test_rejects_browser_approval_channel(self) -> None:
        payload = valid_spec()
        payload["decisions"]["typography"]["approval"]["channel"] = "browser"
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "typography approval must be explicit and conversational",
            result.stdout,
        )

    def test_rejects_accepted_preview_without_session_gallery(self) -> None:
        payload = valid_spec()
        payload["decisions"]["structure"]["preview"]["artifact"] = (
            "../gallery.html"
        )
        self.assertEqual(self.run_validator(payload).returncode, 1)

    def test_rejects_version_two_for_new_full_discovery(self) -> None:
        payload = valid_spec()
        payload["schema_version"] = 2
        result = self.run_validator(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("schema_version must be 3", result.stdout)


if __name__ == "__main__":
    unittest.main()
