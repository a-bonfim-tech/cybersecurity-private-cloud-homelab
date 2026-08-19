from pathlib import Path
import unittest


class ClientDiscriminationRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(
            "research/macos-camera-attribution/"
            "replication/run_client_discrimination.sh"
        )
        cls.text = cls.path.read_text(encoding="utf-8")

    def test_experiment_tag_is_pinned(self):
        self.assertIn(
            'EXPERIMENT_TAG='
            '"macos-camera-client-discrimination-experiment-v1"',
            self.text,
        )

    def test_experiment_commit_is_pinned(self):
        self.assertIn(
            'EXPERIMENT_COMMIT='
            '"cb0ffbfb6ce6996700855fd962745beff5136648"',
            self.text,
        )

    def test_photo_booth_bundle_is_explicit(self):
        self.assertIn(
            'PHOTO_BOOTH_BUNDLE="com.apple.PhotoBooth"',
            self.text,
        )

    def test_three_conditions_exist(self):
        self.assertIn("A: IDLE", self.text)
        self.assertIn("B: QUICKTIME", self.text)
        self.assertIn("C: PHOTO BOOTH", self.text)

    def test_runner_does_not_call_frozen_replication_runner(self):
        self.assertNotIn(
            'run_replication.sh"',
            self.text,
        )

    def test_output_is_namespaced(self):
        self.assertIn(
            'client-discrimination/results',
            self.text,
        )

    def test_claim_boundary_is_explicit(self):
        self.assertIn(
            "not direct frame-delivery evidence",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
