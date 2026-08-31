from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/terraform/validate_plan_json.py"
SPEC = importlib.util.spec_from_file_location("validate_plan_json", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def plan(*changes: tuple[str, list[str]]) -> dict:
    return {
        "format_version": "1.2",
        "resource_changes": [
            {"address": address, "change": {"actions": actions}}
            for address, actions in changes
        ],
    }


EXPECTED = (
    ("proxmox_vm_qemu.bonfim_ai_workload", ["create"]),
    ("proxmox_vm_qemu.pfsense_gateway", ["create"]),
)


class TerraformPlanValidationTests(unittest.TestCase):
    def test_bounded_create_plan_passes_without_values(self) -> None:
        summary = MODULE.validate_plan(plan(*EXPECTED))
        self.assertEqual(summary["validation"], "PASS")
        self.assertEqual(summary["destructive_change_count"], 0)
        self.assertNotIn("planned_values", summary)

    def test_delete_fails_closed(self) -> None:
        changes = (EXPECTED[0], (EXPECTED[1][0], ["delete"]))
        with self.assertRaises(MODULE.PlanValidationError):
            MODULE.validate_plan(plan(*changes))

    def test_replace_fails_closed(self) -> None:
        changes = (EXPECTED[0], (EXPECTED[1][0], ["delete", "create"]))
        with self.assertRaises(MODULE.PlanValidationError):
            MODULE.validate_plan(plan(*changes))

    def test_unexpected_resource_fails_closed(self) -> None:
        changes = EXPECTED + (("proxmox_vm_qemu.unapproved", ["create"]),)
        with self.assertRaises(MODULE.PlanValidationError):
            MODULE.validate_plan(plan(*changes))

    def test_missing_resource_fails_closed(self) -> None:
        with self.assertRaises(MODULE.PlanValidationError):
            MODULE.validate_plan(plan(EXPECTED[0]))

    def test_malformed_plan_fails_closed(self) -> None:
        with self.assertRaises(MODULE.PlanValidationError):
            MODULE.validate_plan({"format_version": "1.2"})


if __name__ == "__main__":
    unittest.main()
