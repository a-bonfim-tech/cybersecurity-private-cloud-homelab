from pathlib import Path
import unittest


class ReplicationResultSchemaTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = Path(
            "research/macos-camera-attribution/"
            "replication/run_replication.sh"
        ).read_text(encoding="utf-8")

        cls.comparator = Path(
            "research/macos-camera-attribution/"
            "replication/compare_runs.py"
        ).read_text(encoding="utf-8")

    def test_comparator_requires_execution_id(self):
        self.assertIn(
            'ap.add_argument("--execution-id", required=True)',
            self.comparator,
        )

    def test_schema_version_is_two(self):
        self.assertIn(
            '"schema_version": 2',
            self.comparator,
        )

    def test_result_contains_execution_id(self):
        self.assertIn(
            '"execution_id": args.execution_id',
            self.comparator,
        )

    def test_result_contains_run_linkage(self):
        self.assertIn(
            '"A1": args.a1.name',
            self.comparator,
        )
        self.assertIn(
            '"B": args.b.name',
            self.comparator,
        )
        self.assertIn(
            '"A2": args.a2.name',
            self.comparator,
        )

    def test_runner_passes_execution_id(self):
        self.assertIn(
            '--execution-id "$EXECUTION_ID"',
            self.runner,
        )


if __name__ == "__main__":
    unittest.main()
