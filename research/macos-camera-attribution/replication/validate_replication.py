#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


OBSERVABLE = "CMIOExtensionStream"

PROHIBITED_RESULT_CLAIMS = (
    "video_frame_delivered",
    "frame was delivered",
    "frame delivered to quicktime",
    "quicktime received a frame",
    "quicktime consumed a frame",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing JSON file: {path}")

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {path}: {exc}")


def require_run(run: Path, label: str) -> None:
    if not run.is_dir():
        fail(f"{label} run directory missing: {run}")

    required = (
        run / "manifest.json",
        run / "derived" / "manifest.json",
        run / "derived" / "timeline.jsonl",
        run / "raw" / "unified.log",
    )

    for path in required:
        if not path.exists():
            fail(f"{label} missing required artifact: {path}")


def count_observable(run: Path) -> int:
    path = run / "raw" / "unified.log"
    text = path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    return len(
        re.findall(
            re.escape(OBSERVABLE),
            text,
            flags=re.IGNORECASE,
        )
    )


def expected_outcome(counts: dict[str, int]) -> str:
    a1 = counts["A1"]
    b = counts["B"]
    a2 = counts["A2"]

    if a1 == 0 and a2 == 0 and b > a1 and b > a2:
        return "REPLICATED"

    if b > a1 and b > a2:
        return "PARTIALLY_REPLICATED"

    return "NOT_REPLICATED"


def validate_result(
    result_path: Path,
    host_id: str,
    counts: dict[str, int],
) -> dict:
    result = load_json(result_path)

    if result.get("schema_version") != 1:
        fail("unsupported result schema_version")

    if result.get("host_id") != host_id:
        fail(
            "result host_id mismatch: "
            f"{result.get('host_id')!r} != {host_id!r}"
        )

    if result.get("observable") != OBSERVABLE:
        fail(
            "unexpected observable: "
            f"{result.get('observable')!r}"
        )

    stored_counts = result.get("counts")

    if stored_counts != counts:
        fail(
            "result count mismatch: "
            f"stored={stored_counts!r} observed={counts!r}"
        )

    expected = expected_outcome(counts)
    actual = result.get("outcome")

    if actual != expected:
        fail(
            "replication outcome mismatch: "
            f"stored={actual!r} expected={expected!r}"
        )

    boundary = str(result.get("claim_boundary", "")).lower()

    if "not direct frame-delivery evidence" not in boundary:
        fail("result does not preserve frame-delivery evidence boundary")

    serialized = json.dumps(result).lower()

    for phrase in PROHIBITED_RESULT_CLAIMS:
        if phrase in serialized:
            fail(
                "result contains prohibited evidence promotion: "
                f"{phrase!r}"
            )

    return result


def validate_host_metadata(
    host_path: Path,
    host_id: str,
) -> None:
    data = load_json(host_path)

    if data.get("host_id") != host_id:
        fail("host metadata host_id mismatch")

    prohibited_keys = {
        "hostname",
        "username",
        "serial",
        "serial_number",
        "platform_uuid",
        "ioplatformuuid",
        "ssid",
        "bssid",
        "ip",
        "ip_address",
        "device_identifier",
        "altdsid",
    }

    present = {
        str(key).lower()
        for key in data
    } & prohibited_keys

    if present:
        fail(
            "host metadata contains prohibited key(s): "
            + ", ".join(sorted(present))
        )


def validate_distinct_runs(
    a1: Path,
    b: Path,
    a2: Path,
) -> None:
    resolved = {
        a1.resolve(),
        b.resolve(),
        a2.resolve(),
    }

    if len(resolved) != 3:
        fail("A1, B and A2 must be three distinct run directories")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Validate a macOS camera-attribution A1/B/A2 replication."
        )
    )

    ap.add_argument("--host-id", required=True)
    ap.add_argument("--a1", type=Path, required=True)
    ap.add_argument("--b", type=Path, required=True)
    ap.add_argument("--a2", type=Path, required=True)
    ap.add_argument("--host", type=Path, required=True)
    ap.add_argument("--result", type=Path, required=True)

    args = ap.parse_args()

    validate_distinct_runs(
        args.a1,
        args.b,
        args.a2,
    )

    require_run(args.a1, "A1")
    require_run(args.b, "B")
    require_run(args.a2, "A2")

    counts = {
        "A1": count_observable(args.a1),
        "B": count_observable(args.b),
        "A2": count_observable(args.a2),
    }

    validate_host_metadata(
        args.host,
        args.host_id,
    )

    result = validate_result(
        args.result,
        args.host_id,
        counts,
    )

    print("===== REPLICATION VALIDATION =====")
    print(f"host_id={args.host_id}")
    print(f"A1={counts['A1']}")
    print(f"B={counts['B']}")
    print(f"A2={counts['A2']}")
    print(f"outcome={result['outcome']}")
    print(
        "pattern="
        f"{counts['A1']} -> "
        f"{counts['B']} -> "
        f"{counts['A2']}"
    )
    print("CLAIM_BOUNDARY=PASS")
    print("HOST_METADATA=PASS")
    print("RUN_DISTINCTNESS=PASS")
    print("REPLICATION_VALIDATION=PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
