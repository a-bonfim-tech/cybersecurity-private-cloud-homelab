from __future__ import annotations

import importlib.util
import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/terraform/write_authorized_tfvars.py"
SPEC = importlib.util.spec_from_file_location("write_authorized_tfvars", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


AUTHORIZED_ENVIRONMENT = {
    "TF_VAR_proxmox_api_url": "https://10.10.70.2:8006/api2/json",
    "TF_VAR_proxmox_api_token_id": "terraform@pve!plan-only",
    "TF_VAR_proxmox_api_token_secret": "synthetic-test-secret",
    "TF_VAR_proxmox_tls_insecure": "false",
    "TF_VAR_target_node": "pve-node-01",
}


class AuthorizedVariableFileTests(unittest.TestCase):
    def test_writes_exact_values_with_mode_0600(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "authorized.tfvars.json"
            values = MODULE.authorized_values(AUTHORIZED_ENVIRONMENT)
            MODULE.write_exclusive(output, values)

            self.assertEqual(json.loads(output.read_text()), values)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertFalse(values["proxmox_tls_insecure"])

    def test_refuses_to_overwrite_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "authorized.tfvars.json"
            output.write_text("existing", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                MODULE.write_exclusive(output, MODULE.authorized_values(AUTHORIZED_ENVIRONMENT))
            self.assertEqual(output.read_text(encoding="utf-8"), "existing")

    def test_rejects_missing_or_insecure_values(self) -> None:
        missing = dict(AUTHORIZED_ENVIRONMENT)
        missing.pop("TF_VAR_proxmox_api_token_secret")
        with self.assertRaises(MODULE.AuthorizedVariableError):
            MODULE.authorized_values(missing)

        insecure = dict(AUTHORIZED_ENVIRONMENT)
        insecure["TF_VAR_proxmox_tls_insecure"] = "true"
        with self.assertRaises(MODULE.AuthorizedVariableError):
            MODULE.authorized_values(insecure)

    def test_explicit_file_outranks_conflicting_automatic_files(self) -> None:
        if not shutil_which("terraform"):
            self.skipTest("terraform is not available")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.tf").write_text(
                'variable "proxmox_tls_insecure" { type = bool }\n',
                encoding="utf-8",
            )
            (root / "terraform.tfvars").write_text(
                "proxmox_tls_insecure = true\n", encoding="utf-8"
            )
            (root / "z.auto.tfvars").write_text(
                "proxmox_tls_insecure = true\n", encoding="utf-8"
            )
            authorized = root / "authorized.tfvars.json"
            authorized.write_text(
                json.dumps({"proxmox_tls_insecure": False}), encoding="utf-8"
            )
            authorized.chmod(0o600)
            result = subprocess.run(
                ["terraform", "console", f"-var-file={authorized}"],
                cwd=root,
                input="var.proxmox_tls_insecure\n",
                capture_output=True,
                check=False,
                text=True,
                env={**os.environ, "TF_IN_AUTOMATION": "1"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "false")

    def test_wrapper_binds_file_and_removes_environment_before_terraform(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            log = root / "terraform.log"
            fake_terraform = fake_bin / "terraform"
            fake_terraform.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
command_name=""
for argument in "$@"; do
  case "$argument" in
    init|plan|show) command_name="$argument" ;;
  esac
done
environment_present=NO
for variable in \
  TF_VAR_proxmox_api_url \
  TF_VAR_proxmox_api_token_id \
  TF_VAR_proxmox_api_token_secret \
  TF_VAR_proxmox_tls_insecure \
  TF_VAR_target_node; do
  if [[ -n "${!variable:-}" ]]; then environment_present=YES; fi
done
printf '%s env_present=%s args=' "$command_name" "$environment_present" >> "$FAKE_TERRAFORM_LOG"
printf '%q ' "$@" >> "$FAKE_TERRAFORM_LOG"
printf '\n' >> "$FAKE_TERRAFORM_LOG"
if [[ "$command_name" == "show" ]]; then
  printf '%s\n' '{"format_version":"1.2","resource_changes":[{"address":"proxmox_vm_qemu.bonfim_ai_workload","change":{"actions":["create"]}},{"address":"proxmox_vm_qemu.pfsense_gateway","change":{"actions":["create"]}}]}'
fi
""",
                encoding="utf-8",
            )
            fake_terraform.chmod(0o700)
            environment = {
                **os.environ,
                **AUTHORIZED_ENVIRONMENT,
                "ALLOW_PROXMOX_PLAN": "YES",
                "FAKE_TERRAFORM_LOG": str(log),
                "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
            }
            result = subprocess.run(
                ["bash", str(ROOT / "tools/terraform/run_sanitized_plan.sh")],
                cwd=ROOT,
                capture_output=True,
                check=False,
                text=True,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["validation"], "PASS")
            log_text = log.read_text(encoding="utf-8")
            self.assertIn("init env_present=NO", log_text)
            self.assertIn("plan env_present=NO", log_text)
            self.assertIn("show env_present=NO", log_text)
            plan_line = next(
                line for line in log_text.splitlines() if line.startswith("plan ")
            )
            self.assertIn("-var-file=", plan_line)
            variable_argument = next(
                item for item in plan_line.split() if item.startswith("-var-file=")
            )
            self.assertFalse(Path(variable_argument.split("=", 1)[1]).exists())
            self.assertNotIn(AUTHORIZED_ENVIRONMENT["TF_VAR_proxmox_api_token_secret"], log_text)


def shutil_which(command: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / command
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


if __name__ == "__main__":
    unittest.main()
