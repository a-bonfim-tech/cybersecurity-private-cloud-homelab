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


def regular_file_inventory(root: Path, exclude: set[Path]) -> set[str]:
    inventory: set[str] = set()
    for path in root.rglob("*"):
        if path in exclude:
            continue
        if path.is_symlink():
            raise ValueError(f"symlinked artifact is not allowed: {path}")
        if path.is_file():
            inventory.add(str(path.relative_to(root.parent)))
    return inventory


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
    if not artifacts:
        return fail("artifacts must not be empty")

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

    raw_dir = run_dir / "raw"
    try:
        raw_inventory = regular_file_inventory(raw_dir, set())
    except ValueError as exc:
        return fail(str(exc))
    if seen != raw_inventory:
        return fail(
            "raw artifact inventory mismatch: "
            f"manifest_only={sorted(seen - raw_inventory)!r} "
            f"filesystem_only={sorted(raw_inventory - seen)!r}"
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

        derived_artifacts = derived_manifest.get("artifacts")
        if not isinstance(derived_artifacts, list):
            return fail("derived artifacts must be an array")
        if not derived_artifacts:
            return fail("derived artifacts must not be empty")

        derived_seen: set[str] = set()
        for item in derived_artifacts:
            if not isinstance(item, dict):
                return fail("derived artifact entry is not an object")
            relative = item.get("path")
            expected = item.get("sha256")

            if not isinstance(relative, str):
                return fail("derived artifact path missing")
            if relative in derived_seen:
                return fail(f"duplicate derived artifact path: {relative}")
            derived_seen.add(relative)

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

        try:
            derived_inventory = regular_file_inventory(
                run_dir / "derived",
                {derived_manifest_path},
            )
        except ValueError as exc:
            return fail(str(exc))
        if derived_seen != derived_inventory:
            return fail(
                "derived artifact inventory mismatch: "
                f"manifest_only={sorted(derived_seen - derived_inventory)!r} "
                f"filesystem_only={sorted(derived_inventory - derived_seen)!r}"
            )

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
