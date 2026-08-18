#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> int:
    print(f"MACOS_EVIDENCE_INTEGRITY=FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <run-directory>", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1]).resolve()
    manifest_path = run_dir / "manifest.json"

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"manifest parse error: {exc}")

    if manifest.get("run_id") != run_dir.name:
        return fail("manifest run_id does not match directory name")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        return fail("artifacts must be an array")

    seen: set[str] = set()

    for item in artifacts:
        if not isinstance(item, dict):
            return fail("artifact entry is not an object")

        relative = item.get("path")
        expected = item.get("sha256")

        if not isinstance(relative, str):
            return fail("artifact path missing")
        if relative in seen:
            return fail(f"duplicate artifact path: {relative}")
        seen.add(relative)

        if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
            return fail(f"invalid SHA-256 for {relative}")

        path = (run_dir / relative).resolve()

        try:
            path.relative_to(run_dir)
        except ValueError:
            return fail(f"path escapes run directory: {relative}")

        if not path.is_file():
            return fail(f"missing artifact: {relative}")

        actual = digest(path)
        if actual != expected:
            return fail(
                f"SHA-256 mismatch for {relative}: "
                f"expected {expected}, got {actual}"
            )

    derived_manifest_path = run_dir / "derived" / "manifest.json"

    if derived_manifest_path.exists():
        try:
            derived_manifest = json.loads(
                derived_manifest_path.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as exc:
            return fail(f"derived manifest parse error: {exc}")

        expected_raw_manifest_hash = derived_manifest.get(
            "source_raw_manifest_sha256"
        )

        if expected_raw_manifest_hash != digest(manifest_path):
            return fail("derived manifest references wrong raw manifest hash")

        for item in derived_manifest.get("artifacts", []):
            relative = item.get("path")
            expected = item.get("sha256")

            if not isinstance(relative, str):
                return fail("derived artifact path missing")

            if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
                return fail(f"invalid derived SHA-256 for {relative}")

            path = (run_dir / relative).resolve()

            try:
                path.relative_to(run_dir)
            except ValueError:
                return fail(f"derived path escapes run directory: {relative}")

            if not path.is_file():
                return fail(f"missing derived artifact: {relative}")

            if digest(path) != expected:
                return fail(f"derived SHA-256 mismatch for {relative}")

    timeline = run_dir / "derived" / "timeline.jsonl"
    if timeline.exists():
        for line_number, raw in enumerate(
            timeline.read_text(encoding="utf-8").splitlines(), 1
        ):
            if not raw.strip():
                continue
            try:
                event = json.loads(raw)
            except json.JSONDecodeError as exc:
                return fail(f"timeline line {line_number}: {exc}")

            if event.get("evidence_class") != "OBSERVED":
                return fail(
                    f"timeline line {line_number}: unexpected evidence_class"
                )

    print(
        "MACOS_EVIDENCE_INTEGRITY=PASS "
        f"run_id={run_dir.name} raw_artifacts={len(artifacts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
