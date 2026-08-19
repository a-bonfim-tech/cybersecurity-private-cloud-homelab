#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path


OBSERVABLE = "CMIOExtensionStream"

CLAIM_BOUNDARY = (
    "Provider stream-related activity only; "
    "not direct frame-delivery evidence."
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"unable to load {path}: {exc}")


def validate_result(
    path: Path,
    result: dict,
    expected_host_id: str,
) -> None:
    if result.get("schema_version") != 2:
        fail(f"{path}: unsupported schema_version")

    if result.get("host_id") != expected_host_id:
        fail(
            f"{path}: host_id mismatch: "
            f"{result.get('host_id')!r}"
        )

    if result.get("observable") != OBSERVABLE:
        fail(f"{path}: observable mismatch")

    if result.get("claim_boundary") != CLAIM_BOUNDARY:
        fail(f"{path}: claim boundary mismatch")

    execution_id = result.get("execution_id")

    if not isinstance(execution_id, str) or not execution_id:
        fail(f"{path}: invalid execution_id")

    counts = result.get("counts")

    if not isinstance(counts, dict):
        fail(f"{path}: missing counts")

    try:
        a1 = counts["A1"]
        b = counts["B"]
        a2 = counts["A2"]
    except KeyError as exc:
        fail(f"{path}: missing count {exc}")

    if not all(
        isinstance(value, int)
        for value in (a1, b, a2)
    ):
        fail(f"{path}: counts must be integers")

    if a1 != 0 or a2 != 0:
        fail(
            f"{path}: control count is non-zero: "
            f"A1={a1}, A2={a2}"
        )

    if b <= 0:
        fail(f"{path}: active-condition count is not positive")

    if result.get("outcome") != "REPLICATED":
        fail(
            f"{path}: outcome is not REPLICATED: "
            f"{result.get('outcome')!r}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize retained same-host macOS camera "
            "replication results."
        )
    )

    parser.add_argument("--host-id", required=True)

    parser.add_argument(
        "--results-dir",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
    )

    args = parser.parse_args()

    paths = sorted(args.results_dir.glob("*.json"))

    if not paths:
        fail(f"no replication results found in {args.results_dir}")

    results: list[dict] = []

    for path in paths:
        document = load(path)

        validate_result(
            path,
            document,
            args.host_id,
        )

        results.append(document)

    execution_ids = [
        result["execution_id"]
        for result in results
    ]

    if len(set(execution_ids)) != len(execution_ids):
        fail("duplicate execution_id detected")

    b_counts = [
        result["counts"]["B"]
        for result in results
    ]

    execution_count = len(results)

    if execution_count >= 3:
        repeatability = "SUPPORTED"
    else:
        repeatability = "INSUFFICIENT_EXECUTIONS"

    summary = {
        "schema_version": 1,
        "host_id": args.host_id,
        "observable": OBSERVABLE,
        "execution_count": execution_count,
        "execution_ids": execution_ids,
        "b_counts": b_counts,
        "b_count_min": min(b_counts),
        "b_count_max": max(b_counts),
        "b_count_mean": statistics.mean(b_counts),
        "all_idle_controls_zero": True,
        "all_active_conditions_positive": True,
        "all_outcomes_replicated": True,
        "same_host_repeatability": repeatability,
        "cross_host_reproducibility": "NOT_TESTED",
        "claim_boundary": CLAIM_BOUNDARY,
        "interpretation": (
            "Repeated same-host association between QuickTime "
            "preview condition and CMIOExtensionStream provider "
            "activity. This does not establish direct frame "
            "delivery or cross-host reproducibility."
        ),
    }

    serialized = (
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    if args.output:
        args.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.output.write_text(
            serialized,
            encoding="utf-8",
        )
    else:
        sys.stdout.write(serialized)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
