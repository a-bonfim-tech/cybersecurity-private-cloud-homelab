from pathlib import Path
import unittest


class ReplicationValidatorSchemaV2Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = Path(
            "research/macos-camera-attribution/"
            "replication/validate_replication.py"
        ).read_text(encoding="utf-8")

        cls.runner = Path(
            "research/macos-camera-attribution/"
            "replication/run_replication.sh"
        ).read_text(encoding="utf-8")

    def test_validator_accepts_execution_id_argument(self):
        self.assertIn(
            'ap.add_argument("--execution-id", required=True)',
            self.validator,
        )

    def test_validator_checks_schema_version_two(self):
        self.assertIn(
            'schema_version',
            self.validator,
        )
        self.assertIn(
            '!= 2',
            self.validator,
        )

    def test_validator_checks_execution_id(self):
        self.assertIn(
            'execution_id',
            self.validator,
        )

    def test_validator_checks_run_linkage(self):
        self.assertIn(
            '"runs"',
            self.validator,
        )

    def test_runner_passes_execution_id_to_validator(self):
        self.assertGreaterEqual(
            self.runner.count(
                '--execution-id "$EXECUTION_ID"'
            ),
            2,
            "execution_id must be sent to both comparator "
            "and replication validator",
        )


if __name__ == "__main__":
    unittest.main()
