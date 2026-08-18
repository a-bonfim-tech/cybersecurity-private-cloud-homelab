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


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <run-directory>", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1]).resolve()
    raw_manifest = run_dir / "manifest.json"
    derived = run_dir / "derived"

    if not raw_manifest.is_file():
        print(f"missing raw manifest: {raw_manifest}", file=sys.stderr)
        return 1

    if not derived.is_dir():
        print(f"missing derived directory: {derived}", file=sys.stderr)
        return 1

    artifacts = []

    for path in sorted(derived.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "manifest.json":
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
        "run_id": run_dir.name,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_raw_manifest": "manifest.json",
        "source_raw_manifest_sha256": sha256(raw_manifest),
        "artifact_class": "DERIVED",
        "artifacts": artifacts,
    }

    output = derived / "manifest.json"
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"derived_manifest={output}")
    print(f"derived_artifacts={len(artifacts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
