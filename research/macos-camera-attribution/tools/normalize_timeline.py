#!/usr/bin/env python3
"""Normalize selected macOS camera/TCC events without promoting interpretations."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


TARGET_BUNDLE = "com.openai.chat"

LINE_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2}(?:\.\d+)?[+-]\d{4})\s+"
    r"\S+\s+"
    r"(?P<process>.+?)\[(?P<pid>\d+)\]:\s+"
    r"(?P<body>.*)$"
)

MSG_ID_RE = re.compile(r"\bmsgID=(?P<msgid>[^,\s]+)")
SERVICE_RE = re.compile(r"\bservice=(?P<service>kTCCService[A-Za-z0-9_]+)")
AUTH_VALUE_RE = re.compile(r"\bauthValue=(?P<value>-?\d+)")
AUTH_REASON_RE = re.compile(r"\bauthReason=(?P<reason>-?\d+)")

RESPONSIBLE_RE = re.compile(
    r"responsible=\{TCCDProcess:\s+identifier=(?P<identifier>[^,\s}]+),"
    r"\s+pid=(?P<pid>\d+)"
)

ACCESSING_RE = re.compile(
    r"accessing=\{TCCDProcess:\s+identifier=(?P<identifier>[^,\s}]+),"
    r"\s+pid=(?P<pid>\d+)"
)

REQUESTING_RE = re.compile(
    r"requesting=\{TCCDProcess:\s+identifier=(?P<identifier>[^,\s}]+),"
    r"\s+pid=(?P<pid>\d+)"
)

CONNECT_CLIENT_RE = re.compile(r"ConnectClient:\s+Added client \[(?P<pid>\d+)\]")


def base_event(
    match: re.Match[str],
    run_id: str,
    event: str,
    body: str,
) -> dict[str, object]:
    return {
        "timestamp": match.group("timestamp"),
        "run_id": run_id,
        "emitter_pid": int(match.group("pid")),
        "emitter_process": match.group("process"),
        "event": event,
        "source": "raw/unified.log",
        "evidence_class": "OBSERVED",
        "confidence": "HIGH",
        "target_related": False,
        "raw_message": body,
    }


def parse_tcc_attribution(body: str) -> dict[str, object]:
    result: dict[str, object] = {}

    for label, regex in (
        ("responsible", RESPONSIBLE_RE),
        ("accessing", ACCESSING_RE),
        ("requesting", REQUESTING_RE),
    ):
        match = regex.search(body)
        if match:
            result[f"{label}_identifier"] = match.group("identifier")
            result[f"{label}_pid"] = int(match.group("pid"))

    identifiers = {
        value
        for key, value in result.items()
        if key.endswith("_identifier") and isinstance(value, str)
    }
    result["target_related"] = TARGET_BUNDLE in identifiers

    return result


def normalize(log_path: Path, run_id: str) -> list[dict[str, object]]:
    parsed_lines: list[tuple[re.Match[str], str]] = []

    for raw in log_path.read_text(
        encoding="utf-8", errors="replace"
    ).splitlines():
        match = LINE_RE.match(raw)
        if match:
            parsed_lines.append((match, match.group("body")))

    # First pass: determine which TCC msgIDs are actually attributable
    # to the target bundle.
    target_tcc_msgids: set[str] = set()

    for _match, body in parsed_lines:
        if "AUTHREQ_ATTRIBUTION" not in body:
            continue

        msg_match = MSG_ID_RE.search(body)
        if not msg_match:
            continue

        attribution = parse_tcc_attribution(body)

        if attribution.get("target_related") is True:
            target_tcc_msgids.add(msg_match.group("msgid"))

    events: list[dict[str, object]] = []

    for match, body in parsed_lines:
        if connect := CONNECT_CLIENT_RE.search(body):
            event = base_event(
                match,
                run_id,
                "camera_provider_client_connected",
                body,
            )
            event["client_pid"] = int(connect.group("pid"))
            event["attribution_scope"] = "provider_client"
            events.append(event)
            continue

        if "ISP_PowerOnCamera" in body:
            event = base_event(match, run_id, "isp_power_on", body)
            event["attribution_scope"] = "hardware_global"
            events.append(event)
            continue

        if "PowerOnCamera" in body:
            event = base_event(match, run_id, "camera_power_on", body)
            event["attribution_scope"] = "hardware_global"
            events.append(event)
            continue

        if "PowerOffCamera" in body:
            event = base_event(match, run_id, "camera_power_off", body)
            event["attribution_scope"] = "hardware_global"
            events.append(event)
            continue

        if "StreamPropertiesForProperties" in body:
            event = base_event(
                match,
                run_id,
                "camera_stream_properties",
                body,
            )
            event["attribution_scope"] = "provider_global"
            events.append(event)
            continue

        if "DevicePropertiesForProperties" in body:
            event = base_event(
                match,
                run_id,
                "camera_device_properties",
                body,
            )
            event["attribution_scope"] = "provider_global"
            events.append(event)
            continue

        if "AvailableProperties" in body:
            event = base_event(
                match,
                run_id,
                "camera_available_properties",
                body,
            )
            event["attribution_scope"] = "provider_global"
            events.append(event)
            continue

        if body.strip() == "Formats":
            event = base_event(
                match,
                run_id,
                "camera_formats_enumerated",
                body,
            )
            event["attribution_scope"] = "provider_global"
            events.append(event)
            continue

        if not any(
            marker in body
            for marker in (
                "AUTHREQ_CTX",
                "AUTHREQ_ATTRIBUTION",
                "AUTHREQ_RESULT",
            )
        ):
            continue

        msg_match = MSG_ID_RE.search(body)
        if not msg_match:
            continue

        msg_id = msg_match.group("msgid")

        # Collector-induced or otherwise unrelated TCC noise is deliberately
        # excluded from the target timeline.
        if msg_id not in target_tcc_msgids:
            continue

        if "AUTHREQ_CTX" in body:
            event = base_event(match, run_id, "tcc_request_context", body)

            service_match = SERVICE_RE.search(body)
            if service_match:
                event["tcc_service"] = service_match.group("service")

            event["tcc_msg_id"] = msg_id
            event["target_related"] = True
            events.append(event)
            continue

        if "AUTHREQ_ATTRIBUTION" in body:
            event = base_event(match, run_id, "tcc_attribution", body)
            event["tcc_msg_id"] = msg_id
            event.update(parse_tcc_attribution(body))
            events.append(event)
            continue

        if "AUTHREQ_RESULT" in body:
            event = base_event(
                match,
                run_id,
                "tcc_authorization_result",
                body,
            )
            event["tcc_msg_id"] = msg_id
            event["target_related"] = True

            if value := AUTH_VALUE_RE.search(body):
                event["auth_value_raw"] = int(value.group("value"))

            if reason := AUTH_REASON_RE.search(body):
                event["auth_reason_raw"] = int(reason.group("reason"))

            events.append(event)

    return events


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <run-directory>", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1]).resolve()
    log_path = run_dir / "raw" / "unified.log"

    if not log_path.is_file():
        print(f"missing {log_path}", file=sys.stderr)
        return 1

    output_dir = run_dir / "derived"
    output_dir.mkdir(exist_ok=True)

    events = normalize(log_path, run_dir.name)

    output = output_dir / "timeline.jsonl"

    with output.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    print(f"events={len(events)}")
    print(f"timeline={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
