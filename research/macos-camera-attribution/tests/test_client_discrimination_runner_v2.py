from pathlib import Path
import unittest


class ClientDiscriminationRunnerV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(
            "research/macos-camera-attribution/"
            "replication/run_client_discrimination_v2.sh"
        )
        cls.text = cls.path.read_text(encoding="utf-8")

    def test_experiment_tag_is_pinned(self):
        self.assertIn(
            'EXPERIMENT_TAG='
            '"macos-camera-client-discrimination-experiment-v2"',
            self.text,
        )

    def test_experiment_commit_is_pinned(self):
        self.assertIn(
            'EXPERIMENT_COMMIT='
            '"784b29e68527011972899ef45975d0788e0cae8b"',
            self.text,
        )

    def test_idle_gate_requires_zero_cmio(self):
        self.assertIn(
            'A_CMIO',
            self.text,
        )
        self.assertIn(
            'ABORTED_CONDITION_INVALID',
            self.text,
        )

    def test_quicktime_gate_requires_document_and_cmio(self):
        self.assertIn(
            'quicktime_document_count',
            self.text,
        )
        self.assertIn(
            'B_CMIO',
            self.text,
        )

    def test_photo_booth_gate_requires_bundle_and_cmio(self):
        self.assertIn(
            'com.apple.PhotoBooth',
            self.text,
        )
        self.assertIn(
            'C_CMIO',
            self.text,
        )

    def test_abort_is_not_inconclusive(self):
        self.assertIn(
            '"ABORTED_CONDITION_INVALID"',
            self.text,
        )

    def test_claim_boundary_is_preserved(self):
        self.assertIn(
            "not direct frame-delivery evidence",
            self.text,
        )

    def test_output_is_v2_namespaced(self):
        self.assertIn(
            "client-discrimination-v2/results",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
