from pathlib import Path
import json
import subprocess
import tempfile
import unittest


MODULE = Path("research/macos-camera-attribution")
SUMMARIZER = MODULE / "replication" / "summarize_replications.py"


def result(
    execution_id: str,
    host_id: str = "host123",
    a1: int = 0,
    b: int = 30,
    a2: int = 0,
    outcome: str = "REPLICATED",
) -> dict:
    return {
        "schema_version": 2,
        "execution_id": execution_id,
        "host_id": host_id,
        "observable": "CMIOExtensionStream",
        "runs": {
            "A1": f"{execution_id}-a1",
            "B": f"{execution_id}-b",
            "A2": f"{execution_id}-a2",
        },
        "counts": {
            "A1": a1,
            "B": b,
            "A2": a2,
        },
        "outcome": outcome,
        "claim_boundary": (
            "Provider stream-related activity only; "
            "not direct frame-delivery evidence."
        ),
    }


class SummarizeReplicationsTests(unittest.TestCase):

    def run_summary(self, documents: list[dict]):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            for index, document in enumerate(documents):
                path = root / f"{index:02d}.json"
                path.write_text(
                    json.dumps(document) + "\n",
                    encoding="utf-8",
                )

            completed = subprocess.run(
                [
                    "python3",
                    str(SUMMARIZER),
                    "--host-id",
                    "host123",
                    "--results-dir",
                    str(root),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            return completed

    def test_four_consistent_replications_support_repeatability(self):
        docs = [
            result("run1", b=30),
            result("run2", b=30),
            result("run3", b=30),
            result("run4", b=30),
        ]

        completed = self.run_summary(docs)

        self.assertEqual(completed.returncode, 0, completed.stderr)

        summary = json.loads(completed.stdout)

        self.assertEqual(summary["execution_count"], 4)
        self.assertEqual(
            summary["same_host_repeatability"],
            "SUPPORTED",
        )
        self.assertEqual(
            summary["cross_host_reproducibility"],
            "NOT_TESTED",
        )
        self.assertEqual(summary["b_counts"], [30, 30, 30, 30])

    def test_nonzero_control_prevents_supported_conclusion(self):
        docs = [
            result("run1"),
            result("run2", a1=1, outcome="PARTIALLY_REPLICATED"),
            result("run3"),
        ]

        completed = self.run_summary(docs)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "control count is non-zero",
            completed.stderr,
        )

    def test_wrong_host_is_rejected(self):
        docs = [
            result("run1"),
            result("run2", host_id="different-host"),
            result("run3"),
        ]

        completed = self.run_summary(docs)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("host_id mismatch", completed.stderr)

    def test_fewer_than_three_runs_is_insufficient(self):
        docs = [
            result("run1"),
            result("run2"),
        ]

        completed = self.run_summary(docs)

        self.assertEqual(completed.returncode, 0, completed.stderr)

        summary = json.loads(completed.stdout)

        self.assertEqual(
            summary["same_host_repeatability"],
            "INSUFFICIENT_EXECUTIONS",
        )

    def test_claim_boundary_is_preserved(self):
        doc = result("run2")
        doc["claim_boundary"] = "Direct frame-delivery evidence."

        completed = self.run_summary([
            result("run1"),
            doc,
            result("run3"),
        ])

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("claim boundary mismatch", completed.stderr)


if __name__ == "__main__":
    unittest.main()
