from pathlib import Path
import unittest


class SecondHostRunbookTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = Path(
            "research/macos-camera-attribution/"
            "replication/run_second_host.sh"
        ).read_text(encoding="utf-8")

    def test_reference_host_is_explicit(self):
        self.assertIn(
            'REFERENCE_HOST_ID="${REFERENCE_HOST_ID:-d2c70c9a2614}"',
            self.text,
        )

    def test_protocol_tag_is_frozen(self):
        self.assertIn(
            'PROTOCOL_TAG="macos-camera-attribution-cross-host-protocol-v1"',
            self.text,
        )

    def test_baseline_tag_is_frozen(self):
        self.assertIn(
            'BASELINE_TAG="macos-camera-attribution-replication-v2"',
            self.text,
        )

    def test_baseline_commit_is_pinned(self):
        self.assertIn(
            'BASELINE_COMMIT='
            '"a0f1ff4264879fe630da047d0ec45762f0fd2dd0"',
            self.text,
        )

    def test_independent_host_gate_precedes_experiment(self):
        gate = self.text.index("check_cross_host.sh")
        run = self.text.index('"$REPL/run_replication.sh"')

        self.assertLess(gate, run)

    def test_baseline_commit_is_verified(self):
        self.assertIn(
            '[[ "$(git rev-parse HEAD)" == "$BASELINE_COMMIT" ]]',
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
