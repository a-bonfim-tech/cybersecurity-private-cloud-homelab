# Purple-Team Runbook 001: Bounded SYN Reconnaissance Simulation

## Objective
Validate Suricata SID `1000001` and the specified Wazuh correlation rule
`100010` when authorized synthetic SYN traffic originates from VLAN 30 and is
directed toward the controlled VLAN 20 test host.

## Scope and safety

- Synthetic lab networks only: `10.10.30.0/24` and `10.10.20.0/24`.
- No Internet, third-party, production or personal data targets.
- Obtain the lab owner's confirmation before enabling the temporary test path.
- The PCAP corpus is synthetic. Suricata offline execution and Wazuh-native
  rule testing are retained as `EXECUTED_SYNTHETIC_TEST_EVIDENCE`. Reference
  nftables policy enforcement is retained separately; native pfSense and live
  packet-path enforcement remain pending.

## Preconditions

1. VLAN 30 source and VLAN 20 target are controlled lab assets.
2. Suricata is installed and SID `1000001` passes configuration validation.
3. A capture interface observes the test path.
4. Wazuh `4.14.7` has the JSON decoder and stock Suricata parent rule `86601`.
5. Exact tool versions and UTC start time are recorded before execution.

## Live lab execution - pending

All commands below are `COMMAND_TO_EXECUTE`. They are not recorded as executed
by this repository version.

```bash
# On the authorized capture point:
sudo tcpdump -i <LAB_CAPTURE_INTERFACE> -nn -s 0 -w recon_vlan30_to_vlan20.pcap \
  'src net 10.10.30.0/24 and dst net 10.10.20.0/24 and tcp'

# From the controlled VLAN 30 source; use only the controlled lab target:
nmap -n -Pn -sS -p 22,80,443,8080 --max-retries 1 --host-timeout 30s \
  10.10.20.15
```

Stop the capture immediately after the bounded test.

## Executed offline detection evidence

On `2026-08-13`, the following bounded procedure was executed locally:

```bash
python3 tools/generate_synthetic_pcaps.py
python3 tools/validate_synthetic_pcaps.py
tools/run_suricata_tests.sh
```

Observed with Suricata `8.0.6 RELEASE`:

- `suricata -T`: passed;
- positive PCAP: nine SYN packets and one SID `1000001` alert;
- below-threshold negative: seven SYN packets and zero SID `1000001` alerts;
- ACK negative: eight ACK packets and zero SID `1000001` alerts.

The rule alerts after the eighth qualifying SYN is exceeded, so the positive
corpus contains nine packets. Evidence is retained under
`docs/evidence/executions/suricata/`.

## Negative test

The two executed controls are bounded regressions. They do not establish a
general false-positive rate.

## Validation commands

```bash
python3 tools/generate_synthetic_pcaps.py
python3 tools/validate_synthetic_pcaps.py
tools/run_suricata_tests.sh
```

## Telemetry & Detection Verification

## Executed Wazuh-native rule evidence

The actual retained `SURICATA-EXEC-001` alert was canonicalized to one JSON
line without semantic changes and passed to Wazuh `4.14.7`:

```bash
tools/run_wazuh_tests.sh
```

Observed native results:

- decoder: `json`;
- matched rule: `100010`;
- level: `7`;
- MITRE technique: `T1046`;
- assertion `100010:7:json`: exit code `0`, `Unit test OK`;
- two bounded negative controls: zero matches for rule `100010`.

The initial native run proved that `<if_group>json</if_group>` did not follow
the Wazuh Suricata rule chain. Rule `100010` was minimally corrected to inherit
from stock rule `86601` using `<if_sid>86601</if_sid>`, then all tests were
repeated successfully.

This proves preprocessing, JSON decoding and rule evaluation. It does not
prove an operating Wazuh manager ingestion pipeline, alert persistence,
firewall enforcement or control effectiveness.

## Evidence state

The evidence manifest records the observed output:

1. Suricata configuration result and exact version.
2. Positive and negative PCAP hashes.
3. minimized Suricata alert and matching SID;
4. Wazuh-native positive assertion and bounded negative controls;
5. Reference nftables enforcement results and counters, retained separately
   from this detection run.

An IDS alert does not prove that the firewall blocked the packet.

## Result classification

- `SPECIFICATION_ONLY`: procedure or test vector exists but was not executed.
- `VALIDATED`: syntax or file structure was checked.
- `EXECUTED_SYNTHETIC_TEST_EVIDENCE`: the procedure ran and retained output.
- `EFFECTIVE`: requires repeatable operating evidence beyond this runbook.

## Cleanup

1. Remove any temporary firewall exception.
2. Stop capture and test processes.
3. Confirm the VLAN 30 default-deny baseline is restored.
4. Remove transient tool output that contains unnecessary host details.
5. Retain only minimized synthetic evidence and its hashes.

## Independent reproduction gate

CI regenerates the deterministic corpus and repeats Suricata configuration,
positive and negative tests. Wazuh-native CI reproduction is performed by a
separate isolated container gate. Reference nftables policy enforcement has
executed in an isolated four-zone harness; native pfSense enforcement and the
unified live packet path remain pending.

```text
SURICATA_OFFLINE_EXECUTION=EXECUTED
WAZUH_LOGTEST_EXECUTION=EXECUTED
WAZUH_MANAGER_OPERATION=PENDING
REFERENCE_NFTABLES_ENFORCEMENT=EXECUTED_SYNTHETIC_TEST_EVIDENCE
PFSENSE_NATIVE_ENFORCEMENT=PENDING
UNIFIED_LIVE_PACKET_PATH=PENDING
```
