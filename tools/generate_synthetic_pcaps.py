#!/usr/bin/env python3
"""Generate deterministic synthetic Ethernet/IPv4/TCP PCAP test vectors."""

from __future__ import annotations

import ipaddress
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PCAP_DIR = ROOT / "docs" / "evidence" / "pcaps"
SRC_IP = ipaddress.IPv4Address("10.10.30.5").packed
DST_IP = ipaddress.IPv4Address("10.10.20.15").packed
SRC_MAC = bytes.fromhex("020000000030")
DST_MAC = bytes.fromhex("020000000020")
BASE_EPOCH = 1_700_000_000
PORTS = (22, 80, 443, 8080)


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    words = struct.unpack(f"!{len(data) // 2}H", data)
    total = sum(words)
    total = (total & 0xFFFF) + (total >> 16)
    total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def tcp_frame(index: int, destination_port: int, flags: int) -> bytes:
    source_port = 40_000 + index
    sequence = 1_000 + index
    tcp_without_checksum = struct.pack(
        "!HHLLBBHHH",
        source_port,
        destination_port,
        sequence,
        0,
        5 << 4,
        flags,
        64_240,
        0,
        0,
    )
    pseudo_header = SRC_IP + DST_IP + struct.pack("!BBH", 0, 6, 20)
    tcp_checksum = checksum(pseudo_header + tcp_without_checksum)
    tcp_header = struct.pack(
        "!HHLLBBHHH",
        source_port,
        destination_port,
        sequence,
        0,
        5 << 4,
        flags,
        64_240,
        tcp_checksum,
        0,
    )

    ip_without_checksum = struct.pack(
        "!BBHHHBBH4s4s",
        0x45,
        0,
        40,
        0x2000 + index,
        0x4000,
        64,
        6,
        0,
        SRC_IP,
        DST_IP,
    )
    ip_header = ip_without_checksum[:10] + struct.pack(
        "!H", checksum(ip_without_checksum)
    ) + ip_without_checksum[12:]
    ethernet_header = DST_MAC + SRC_MAC + struct.pack("!H", 0x0800)
    return ethernet_header + ip_header + tcp_header


def write_pcap(path: Path, packets: list[tuple[int, int, bytes]]) -> None:
    global_header = struct.pack(
        "<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65_535, 1
    )
    data = bytearray(global_header)
    for seconds, microseconds, packet in packets:
        data.extend(struct.pack("<IIII", seconds, microseconds, len(packet), len(packet)))
        data.extend(packet)
    path.write_bytes(data)


def packet_series(count: int, flags: int) -> list[tuple[int, int, bytes]]:
    return [
        (
            BASE_EPOCH,
            index * 100_000,
            tcp_frame(index, PORTS[index % len(PORTS)], flags),
        )
        for index in range(count)
    ]


def main() -> None:
    PCAP_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "recon_vlan30_to_vlan20_positive_scan.pcap": packet_series(8, 0x02),
        "recon_vlan30_to_vlan20_negative_below_threshold.pcap": packet_series(7, 0x02),
        "recon_vlan30_to_vlan20_negative_ack.pcap": packet_series(8, 0x10),
    }
    for name, packets in outputs.items():
        write_pcap(PCAP_DIR / name, packets)
        print(f"{name}: packets={len(packets)}")


if __name__ == "__main__":
    main()
