from pathlib import Path
import unittest


class ReplicationResultIdentityTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = Path(
            "research/macos-camera-attribution/"
            "replication/run_replication.sh"
        ).read_text(encoding="utf-8")

    def test_result_identity_must_not_be_host_id_only(self):
        self.assertNotIn(
            'RESULT="$REPL/results/${HOST_ID}.json"',
            self.runner,
        )

    def test_execution_id_is_generated(self):
        self.assertIn(
            "date -u '+%Y%m%dT%H%M%SZ'",
            self.runner,
        )

    def test_results_are_namespaced_by_host(self):
        self.assertIn(
            'RESULT_DIR="$REPL/results/$HOST_ID"',
            self.runner,
        )

    def test_result_is_keyed_by_execution_id(self):
        self.assertIn(
            'RESULT="$RESULT_DIR/${EXECUTION_ID}.json"',
            self.runner,
        )

    def test_result_directory_is_created(self):
        self.assertIn(
            'mkdir -p "$RESULT_DIR"',
            self.runner,
        )


if __name__ == "__main__":
    unittest.main()
