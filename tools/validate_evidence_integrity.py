#!/usr/bin/env python3
"""Validate retained evidence integrity without modifying repository files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs/evidence/evidence-manifest.json"
EVIDENCE_ROOT = ROOT / "docs/evidence"
RULE_ARTIFACTS = {"100010": ROOT / "detections/wazuh/local_rules.xml"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ValidationError(Exception):
    """An actionable evidence-integrity failure."""


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def repository_path(value: str, field: str, evidence_id: str) -> Path:
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValidationError(
            f"{evidence_id}: {field} escapes repository root: {value}"
        ) from exc
    if not path.is_file():
        raise ValidationError(f"{evidence_id}: missing {field}: {value}")
    return path


def verify_hash(path: Path, expected: str, context: str) -> None:
    if not SHA256_RE.fullmatch(expected):
        raise ValidationError(f"{context}: invalid SHA-256 value: {expected!r}")
    actual = digest(path)
    if actual != expected:
        raise ValidationError(
            f"{context}: SHA-256 mismatch for {path.relative_to(ROOT)}; "
            f"expected {expected}, got {actual}"
        )


def validate_manifest(manifest_path: Path) -> tuple[int, int]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"manifest parse failed: {exc}") from exc
    items = manifest.get("evidence_items")
    if not isinstance(items, list):
        raise ValidationError("manifest evidence_items must be an array")

    seen: set[str] = set()
    hashes = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValidationError(f"evidence_items[{index}] must be an object")
        evidence_id = item.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id:
            raise ValidationError(f"evidence_items[{index}] has no evidence_id")
        if evidence_id in seen:
            raise ValidationError(f"duplicate evidence_id: {evidence_id}")
        seen.add(evidence_id)

        for path_field, hash_field in (
            ("input_path", "input_sha256"),
            ("output_path", "output_sha256"),
        ):
            value = item.get(path_field)
            expected = item.get(hash_field)
            if value is not None:
                if not isinstance(value, str) or not value:
                    raise ValidationError(f"{evidence_id}: invalid {path_field}")
                path = repository_path(value, path_field, evidence_id)
                if expected is not None:
                    if not isinstance(expected, str):
                        raise ValidationError(f"{evidence_id}: invalid {hash_field}")
                    verify_hash(path, expected, f"{evidence_id}:{hash_field}")
                    hashes += 1
            elif expected is not None:
                raise ValidationError(
                    f"{evidence_id}: {hash_field} declared without {path_field}"
                )

        rule_hash = item.get("rule_sha256")
        if rule_hash is not None:
            rule_id = str(item.get("rule_id", ""))
            declared_rule_path = item.get("rule_path")
            if declared_rule_path is not None:
                if not isinstance(declared_rule_path, str):
                    raise ValidationError(
                        f"{evidence_id}: invalid rule_path"
                    )
                rule_path = repository_path(
                    declared_rule_path,
                    "rule_path",
                    evidence_id,
                )
            else:
                rule_path = RULE_ARTIFACTS.get(rule_id)
            if rule_path is None:
                raise ValidationError(
                    f"{evidence_id}: no deterministic rule artifact for rule_id {rule_id!r}"
                )
            if not isinstance(rule_hash, str):
                raise ValidationError(f"{evidence_id}: invalid rule_sha256")
            verify_hash(rule_path, rule_hash, f"{evidence_id}:rule_sha256")
            hashes += 1
    return len(items), hashes


def validate_sha256sums() -> tuple[int, int]:
    files = sorted(EVIDENCE_ROOT.rglob("SHA256SUMS"))
    entries = 0
    for sums_file in files:
        for line_number, raw in enumerate(
            sums_file.read_text(encoding="utf-8").splitlines(), 1
        ):
            if not raw.strip():
                continue
            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", raw)
            if not match:
                raise ValidationError(
                    f"{sums_file.relative_to(ROOT)}:{line_number}: malformed entry"
                )
            expected, name = match.groups()
            if name.startswith("*"):
                name = name[1:]
            path = (sums_file.parent / name).resolve()
            try:
                path.relative_to(sums_file.parent.resolve())
            except ValueError as exc:
                raise ValidationError(
                    f"{sums_file.relative_to(ROOT)}:{line_number}: path escapes directory"
                ) from exc
            if not path.is_file():
                raise ValidationError(
                    f"{sums_file.relative_to(ROOT)}:{line_number}: missing {name}"
                )
            verify_hash(path, expected, f"{sums_file.relative_to(ROOT)}:{line_number}")
            entries += 1
    return len(files), entries


def validate_json_evidence() -> tuple[int, int]:
    json_files = sorted(EVIDENCE_ROOT.rglob("*.json"))
    jsonl_files = sorted(EVIDENCE_ROOT.rglob("*.jsonl"))
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError(f"{path.relative_to(ROOT)}: JSON parse failed: {exc}") from exc
    for path in jsonl_files:
        for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValidationError(
                    f"{path.relative_to(ROOT)}:{line_number}: JSONL parse failed: {exc}"
                ) from exc
    return len(json_files), len(jsonl_files)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    try:
        evidence_count, hash_count = validate_manifest(manifest_path)
        sums_count, sums_entries = validate_sha256sums()
        json_count, jsonl_count = validate_json_evidence()
    except ValidationError as exc:
        print(f"EVIDENCE_INTEGRITY=FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        "EVIDENCE_INTEGRITY=PASS "
        f"evidence_ids={evidence_count} manifest_hashes={hash_count} "
        f"sha256sums_files={sums_count} sha256sums_entries={sums_entries} "
        f"json_files={json_count} jsonl_files={jsonl_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
