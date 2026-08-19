#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PATTERN = re.compile(r"CMIOExtensionStream", re.I)

def count_raw(run: Path) -> int:
    raw = run / "raw" / "unified.log"
    if not raw.exists():
        raise FileNotFoundError(raw)
    return len(PATTERN.findall(raw.read_text(
        encoding="utf-8",
        errors="replace",
    )))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host-id", required=True)
    ap.add_argument("--execution-id", required=True)
    ap.add_argument("--a1", type=Path, required=True)
    ap.add_argument("--b", type=Path, required=True)
    ap.add_argument("--a2", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    counts = {
        "A1": count_raw(args.a1),
        "B": count_raw(args.b),
        "A2": count_raw(args.a2),
    }

    if (
        counts["B"] > counts["A1"]
        and counts["B"] > counts["A2"]
        and counts["A1"] == 0
        and counts["A2"] == 0
    ):
        outcome = "REPLICATED"
    elif (
        counts["B"] > counts["A1"]
        and counts["B"] > counts["A2"]
    ):
        outcome = "PARTIALLY_REPLICATED"
    else:
        outcome = "NOT_REPLICATED"

    result = {
        "schema_version": 2,
        "execution_id": args.execution_id,
        "host_id": args.host_id,
        "observable": "CMIOExtensionStream",
        "runs": {
            "A1": args.a1.name,
            "B": args.b.name,
            "A2": args.a2.name,
        },
        "counts": counts,
        "outcome": outcome,
        "claim_boundary": (
            "Provider stream-related activity only; "
            "not direct frame-delivery evidence."
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
