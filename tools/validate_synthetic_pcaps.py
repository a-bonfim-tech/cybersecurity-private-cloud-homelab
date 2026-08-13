#!/usr/bin/env python3
"""Validate deterministic corpus metadata without third-party dependencies."""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PCAP_DIR = ROOT / "docs" / "evidence" / "pcaps"
EXPECTED = {
    "recon_vlan30_to_vlan20_positive_scan.pcap": {"packets": 9, "flags": 0x02},
    "recon_vlan30_to_vlan20_negative_below_threshold.pcap": {"packets": 7, "flags": 0x02},
    "recon_vlan30_to_vlan20_negative_ack.pcap": {"packets": 8, "flags": 0x10},
}


def inspect(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    if len(data) < 24 or data[:4] != bytes.fromhex("d4c3b2a1"):
        raise ValueError(f"invalid little-endian PCAP: {path}")
    offset = 24
    packets = []
    while offset < len(data):
        seconds, microseconds, captured, original = struct.unpack_from(
            "<IIII", data, offset
        )
        offset += 16
        frame = data[offset : offset + captured]
        offset += captured
        if captured != original or len(frame) != captured:
            raise ValueError(f"truncated packet in {path}")
        packets.append(
            {
                "seconds": seconds,
                "microseconds": microseconds,
                "source": ".".join(str(value) for value in frame[26:30]),
                "destination": ".".join(str(value) for value in frame[30:34]),
                "destination_port": struct.unpack("!H", frame[36:38])[0],
                "flags": frame[47],
            }
        )
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "packet_count": len(packets),
        "packets": packets,
    }


def main() -> None:
    reports = []
    for name, expected in EXPECTED.items():
        report = inspect(PCAP_DIR / name)
        assert report["packet_count"] == expected["packets"]
        packets = report["packets"]
        assert all(packet["source"] == "10.10.30.5" for packet in packets)
        assert all(packet["destination"] == "10.10.20.15" for packet in packets)
        assert all(packet["destination_port"] in {22, 80, 443, 8080} for packet in packets)
        assert all(packet["flags"] == expected["flags"] for packet in packets)
        assert all(packet["seconds"] == 1_700_000_000 for packet in packets)
        reports.append(report)
    json.dump(reports, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
