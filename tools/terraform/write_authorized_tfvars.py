#!/usr/bin/env python3
"""Bind checked environment values into one protected Terraform variable file."""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path


REQUIRED_ENVIRONMENT = {
    "proxmox_api_url": "TF_VAR_proxmox_api_url",
    "proxmox_api_token_id": "TF_VAR_proxmox_api_token_id",
    "proxmox_api_token_secret": "TF_VAR_proxmox_api_token_secret",
    "target_node": "TF_VAR_target_node",
}


class AuthorizedVariableError(Exception):
    """Authorized variables cannot be safely materialized."""


def authorized_values(environment: dict[str, str]) -> dict[str, object]:
    values: dict[str, object] = {}
    for terraform_name, environment_name in REQUIRED_ENVIRONMENT.items():
        value = environment.get(environment_name, "")
        if not value:
            raise AuthorizedVariableError(f"missing {environment_name}")
        values[terraform_name] = value

    tls_value = environment.get("TF_VAR_proxmox_tls_insecure", "false")
    if tls_value != "false":
        raise AuthorizedVariableError("TLS verification must remain enabled")
    values["proxmox_tls_insecure"] = False
    return values


def write_exclusive(path: Path, values: dict[str, object]) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(values, handle, sort_keys=True)
            handle.write("\n")
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    if stat.S_IMODE(path.stat().st_mode) != 0o600:
        path.unlink(missing_ok=True)
        raise AuthorizedVariableError("authorized variable file mode is not 0600")


def main() -> int:
    if len(sys.argv) != 2:
        print("AUTHORIZED_TFVARS=FAIL: expected one output path", file=sys.stderr)
        return 2
    output = Path(sys.argv[1])
    try:
        values = authorized_values(dict(os.environ))
        write_exclusive(output, values)
    except (AuthorizedVariableError, OSError) as exc:
        print(f"AUTHORIZED_TFVARS=FAIL: {exc}", file=sys.stderr)
        return 1
    print("AUTHORIZED_TFVARS=CREATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
