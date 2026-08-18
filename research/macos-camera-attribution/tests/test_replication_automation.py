from pathlib import Path
import hashlib
import re
import unittest


MODULE = Path(__file__).resolve().parents[1]
RUNNER = MODULE / "replication" / "run_replication.sh"


class ReplicationAutomationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = RUNNER.read_text(encoding="utf-8")

    def test_runner_contains_single_derive_host_id(self):
        count = len(
            re.findall(
                r"(?m)^derive_host_id\(\)\s*\{",
                self.text,
            )
        )
        self.assertEqual(count, 1)

    def test_runner_contains_single_collect_scenario(self):
        count = len(
            re.findall(
                r"(?m)^collect_scenario\(\)\s*\{",
                self.text,
            )
        )
        self.assertEqual(count, 1)

    def test_host_id_uses_newline_not_literal_backslash_n(self):
        self.assertIn(
            """printf '%s\\n' "$uuid" \\""".rstrip("\\"),
            self.text,
        )

        self.assertNotIn(
            """printf '%s\\\\n' "$uuid" """,
            self.text,
        )

    def test_host_id_reference_semantics(self):
        sample_uuid = "7E68ED91-569F-5585-A588-8A53F31E94DF"

        expected = hashlib.sha256(
            (sample_uuid + "\n").encode("utf-8")
        ).hexdigest()[:12]

        without_newline = hashlib.sha256(
            sample_uuid.encode("utf-8")
        ).hexdigest()[:12]

        literal_backslash_n = hashlib.sha256(
            (sample_uuid + r"\n").encode("utf-8")
        ).hexdigest()[:12]

        self.assertNotEqual(expected, without_newline)
        self.assertNotEqual(expected, literal_backslash_n)

    def test_collect_scenario_keeps_operational_output_off_stdout(self):
        block_match = re.search(
            r"(?ms)^collect_scenario\(\)\s*\{.*?^\}",
            self.text,
        )

        self.assertIsNotNone(block_match)

        block = block_match.group(0)

        self.assertIn(
            '"$COLLECTOR" "$scenario" "$seconds" >&2',
            block,
        )

        self.assertIn(
            'process_run "$run" "$label" >&2',
            block,
        )

        self.assertIn(
            'printf \'%s\\n\' "$run"',
            block,
        )

    def test_existing_host_metadata_is_not_overwritten(self):
        expected = '''if [[ -f "$HOST_FILE" ]]; then
    printf 'host_metadata=existing\\n'
else
    capture_host_metadata "$HOST_FILE" "$HOST_ID"
    printf 'host_metadata=created\\n'
fi'''

        self.assertIn(expected, self.text)


if __name__ == "__main__":
    unittest.main()
