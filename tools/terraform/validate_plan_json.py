#!/usr/bin/env python3
"""Emit a secret-free summary only for an explicitly bounded Terraform plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


EXPECTED_ADDRESSES = {
    "proxmox_vm_qemu.bonfim_ai_workload",
    "proxmox_vm_qemu.pfsense_gateway",
}
ALLOWED_ACTIONS = {("create",), ("no-op",), ("read",)}


class PlanValidationError(Exception):
    """The plan is malformed, destructive, or outside the approved boundary."""


def load_plan(path: Path) -> dict:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanValidationError(f"plan JSON could not be read: {exc}") from exc
    if not isinstance(document, dict):
        raise PlanValidationError("plan JSON root must be an object")
    return document


def validate_plan(document: dict) -> dict:
    if not isinstance(document.get("format_version"), str):
        raise PlanValidationError("format_version is missing")
    changes = document.get("resource_changes")
    if not isinstance(changes, list):
        raise PlanValidationError("resource_changes must be an array")

    observed: dict[str, list[str]] = {}
    for index, item in enumerate(changes):
        if not isinstance(item, dict):
            raise PlanValidationError(f"resource_changes[{index}] must be an object")
        address = item.get("address")
        change = item.get("change")
        actions = change.get("actions") if isinstance(change, dict) else None
        if not isinstance(address, str) or not isinstance(actions, list):
            raise PlanValidationError(f"resource_changes[{index}] is incomplete")
        action_tuple = tuple(actions)
        if address not in EXPECTED_ADDRESSES:
            raise PlanValidationError(f"unexpected resource address: {address}")
        if action_tuple not in ALLOWED_ACTIONS:
            raise PlanValidationError(
                f"disallowed action for {address}: {','.join(map(str, actions))}"
            )
        if address in observed:
            raise PlanValidationError(f"duplicate resource address: {address}")
        observed[address] = actions

    if set(observed) != EXPECTED_ADDRESSES:
        missing = sorted(EXPECTED_ADDRESSES - set(observed))
        raise PlanValidationError(f"expected resource missing from plan: {','.join(missing)}")

    counts = {"create": 0, "no-op": 0, "read": 0}
    for actions in observed.values():
        counts[actions[0]] += 1
    return {
        "claim_boundary": "PLAN_ONLY_NO_APPLY_OR_OPERATIONAL_EFFECTIVENESS_CLAIM",
        "destructive_change_count": 0,
        "resource_change_count": len(observed),
        "action_counts": counts,
        "resources": [
            {"address": address, "actions": observed[address]}
            for address in sorted(observed)
        ],
        "validation": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan_json", type=Path)
    args = parser.parse_args()
    try:
        summary = validate_plan(load_plan(args.plan_json))
    except PlanValidationError as exc:
        print(f"TERRAFORM_PLAN_VALIDATION=FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
