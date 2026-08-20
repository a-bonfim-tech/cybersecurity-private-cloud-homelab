from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path("research/macos-camera-attribution")
VALIDATOR = ROOT / "tools" / "validate_module.py"
REPLICATION_VALIDATOR = ROOT / "replication" / "validate_replication.py"


class SecurityHardeningTests(unittest.TestCase):
    def run_validator(self, run: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(VALIDATOR), str(run)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_collector_requires_private_exclusive_run_directory(self):
        collector = (ROOT / "tools" / "collect_run.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("umask 077", collector)
        self.assertIn('if ! mkdir "$RUN_DIR"', collector)
        self.assertNotIn('mkdir -p "$RAW"', collector)

    def test_module_validator_rejects_empty_artifact_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "run"
            run.mkdir()
            (run / "manifest.json").write_text(
                json.dumps({"run_id": "run", "artifacts": []}),
                encoding="utf-8",
            )
            result = self.run_validator(run)
            self.assertEqual(result.returncode, 1)
            self.assertIn("artifacts must not be empty", result.stderr)

    def test_module_validator_rejects_uncovered_raw_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "run"
            raw = run / "raw"
            raw.mkdir(parents=True)
            artifact = raw / "covered.txt"
            artifact.write_text("covered\n", encoding="utf-8")
            (raw / "uncovered.txt").write_text("uncovered\n", encoding="utf-8")
            (run / "manifest.json").write_text(
                json.dumps(
                    {
                        "run_id": "run",
                        "artifacts": [
                            {
                                "path": "raw/covered.txt",
                                "sha256": hashlib.sha256(
                                    artifact.read_bytes()
                                ).hexdigest(),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_validator(run)
            self.assertEqual(result.returncode, 1)
            self.assertIn("raw artifact inventory mismatch", result.stderr)

    def test_replication_validator_rejects_nested_private_identifier(self):
        spec = importlib.util.spec_from_file_location(
            "validate_replication_security_test",
            REPLICATION_VALIDATOR,
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as tmp:
            host = Path(tmp) / "host.json"
            host.write_text(
                json.dumps(
                    {
                        "host_id": "reference",
                        "details": {"username": "must-not-pass"},
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit):
                module.validate_host_metadata(host, "reference")

    def test_wazuh_frequency_rule_correlates_same_source(self):
        rules = Path("detections/wazuh/local_rules.xml").read_text(
            encoding="utf-8"
        )
        frequency_rule = rules.split('<rule id="100002"', 1)[1].split(
            "</rule>", 1
        )[0]
        self.assertIn("<same_srcip />", frequency_rule)

    def test_historical_wazuh_execution_pins_its_rule_artifact(self):
        manifest = json.loads(
            Path("docs/evidence/evidence-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        item = next(
            entry
            for entry in manifest["evidence_items"]
            if entry["evidence_id"] == "WAZUH-EXEC-001"
        )
        rule = Path(item["rule_path"])
        self.assertTrue(rule.is_file())
        self.assertEqual(
            hashlib.sha256(rule.read_bytes()).hexdigest(),
            item["rule_sha256"],
        )

    def test_second_host_runner_uses_disposable_worktree(self):
        runner = (ROOT / "replication" / "run_second_host.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn('git worktree add --detach "$WORKTREE"', runner)
        self.assertIn('worktree remove --force "$WORKTREE"', runner)


if __name__ == "__main__":
    unittest.main()
