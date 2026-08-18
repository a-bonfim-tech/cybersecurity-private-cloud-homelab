from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "normalize_timeline.py"

SPEC = importlib.util.spec_from_file_location("normalize_timeline", MODULE_PATH)
assert SPEC is not None
assert SPEC.loader is not None

module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class NormalizeTimelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = (
            ROOT / "tests" / "fixtures" / "unified-log-sanitized.log"
        )

    def test_known_camera_events_are_normalized(self) -> None:
        events = module.normalize(self.fixture, "RUN-TEST-001")
        names = [event["event"] for event in events]

        self.assertIn("camera_provider_client_connected", names)
        self.assertIn("isp_power_on", names)
        self.assertIn("camera_power_off", names)

    def test_connect_client_preserves_client_pid(self) -> None:
        events = module.normalize(self.fixture, "RUN-TEST-002")

        event = next(
            event
            for event in events
            if event["event"] == "camera_provider_client_connected"
        )

        self.assertEqual(event["emitter_pid"], 543)
        self.assertEqual(event["client_pid"], 2091)

    def test_target_tcc_chain_is_retained(self) -> None:
        events = module.normalize(self.fixture, "RUN-TEST-003")

        target_events = [
            event
            for event in events
            if event.get("tcc_msg_id") == "2091.4"
        ]

        self.assertEqual(len(target_events), 3)
        self.assertTrue(
            all(event["target_related"] is True for event in target_events)
        )

    def test_collector_tcc_noise_is_excluded(self) -> None:
        events = module.normalize(self.fixture, "RUN-TEST-004")

        self.assertFalse(
            any(
                event.get("tcc_msg_id") == "7350.5"
                for event in events
            )
        )

    def test_raw_tcc_numeric_values_are_not_interpreted(self) -> None:
        events = module.normalize(self.fixture, "RUN-TEST-005")

        result = next(
            event
            for event in events
            if event["event"] == "tcc_authorization_result"
        )

        self.assertEqual(result["auth_value_raw"], 1)
        self.assertEqual(result["auth_reason_raw"], 5)

        self.assertNotIn("authorized", result)
        self.assertNotIn("meaning", result)

    def test_no_frame_delivery_is_invented(self) -> None:
        events = module.normalize(self.fixture, "RUN-TEST-006")

        self.assertFalse(
            any(
                event["event"] == "video_frame_delivered"
                for event in events
            )
        )

    def test_direct_observations_are_not_promoted(self) -> None:
        events = module.normalize(self.fixture, "RUN-TEST-007")

        for event in events:
            self.assertEqual(event["evidence_class"], "OBSERVED")
            self.assertEqual(event["confidence"], "HIGH")


if __name__ == "__main__":
    unittest.main()
