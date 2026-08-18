#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return None


def parse_metadata(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.is_file():
        return result

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key] = value
    return result


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <run-directory>", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1]).resolve()
    raw = run_dir / "raw"

    if not raw.is_dir():
        print(f"missing raw directory: {raw}", file=sys.stderr)
        return 1

    metadata = parse_metadata(raw / "run-metadata.txt")

    artifacts = []
    for path in sorted(raw.rglob("*")):
        if not path.is_file():
            continue

        artifacts.append(
            {
                "path": str(path.relative_to(run_dir)),
                "size": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    manifest = {
        "manifest_version": "1.0.0",
        "run_id": metadata.get("run_id"),
        "scenario": metadata.get("scenario"),
        "start_utc": metadata.get("start_utc"),
        "end_utc": metadata.get("end_utc"),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "OBSERVED",
        "control_valid": parse_bool(metadata.get("control_valid")),
        "control_invalid_reason": metadata.get("control_invalid_reason"),
        "raw_evidence_mutability_policy": "DO_NOT_MODIFY_AFTER_MANIFEST",
        "artifacts": artifacts,
    }

    output = run_dir / "manifest.json"
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"manifest={output}")
    print(f"artifacts={len(artifacts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
