# Baseline Firewall Policy Specification

## Scope and evidence boundary

This document defines the intended inter-zone policy. It does not prove that a
firewall configuration has been applied or that a control is effective.

| VLAN | Name | CIDR | Intended purpose |
| :--- | :--- | :--- | :--- |
| 10 | TRUSTED | `10.10.10.0/24` | Administrative access and identity services |
| 20 | SERVERS | `10.10.20.0/24` | Hosted workloads |
| 30 | CYBER LAB | `10.10.30.0/24` | Isolated, authorized synthetic testing |
| 40 | MONITORING | `10.10.40.0/24` | Passive sensors and security telemetry |

## Policy invariants

1. Inter-zone traffic is denied unless an explicit rule allows it.
2. VLAN 30 must not initiate production or Internet attack traffic.
3. Monitoring access is limited to telemetry flows and administration from
   VLAN 10.
4. An exception requires an owner, expiry date and evidence reference.
5. `DESIGNED` means policy intent only; it is not enforcement evidence.

## Inter-zone rule matrix

| ID | Source | Destination | Protocol | Port / service | Action | Justification | Owner | Logging | Exception | Positive test | Negative test | Evidence reference | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| FW-001 | VLAN 10 | VLAN 20 | TCP | 22 / SSH | ALLOW | Bounded server administration | Homelab administrator | Session start and deny events | None | Authorized admin source reaches SSH | VLAN 30 cannot reach SSH | Pending | DESIGNED |
| FW-002 | VLAN 20 | VLAN 40 | TCP | 1514 / Wazuh agent | ALLOW | Forward security telemetry | Homelab administrator | Connection and deny events | None | Agent sends synthetic event | Other destination port is denied | Pending | DESIGNED |
| FW-003 | VLAN 40 | VLAN 20 | L2 mirror | SPAN / TAP | ALLOW | Passive network observation | Homelab administrator | Sensor health | Physical or virtual mirror configuration | Sensor receives test packet | Sensor cannot initiate session to workload | Pending | DESIGNED |
| FW-004 | VLAN 30 | VLAN 20 | TCP | 22, 80, 443, 8080 | DENY | Isolate the authorized attack-simulation zone | Homelab administrator | All matching denies | Temporary test exception must be time-bound | Synthetic probe is denied and logged | Benign traffic inside VLAN 30 is unaffected | `PCAP-001` is a specification, not enforcement evidence | DESIGNED |
| FW-005 | Any zone | Any other zone | Any | Any | DENY | Default-deny inter-zone baseline | Homelab administrator | All denies | Explicit rules above only | Unlisted flow is denied | Explicit allow remains usable | Pending | DESIGNED |

## Validation gate

Promotion from `DESIGNED` to `TESTED` requires a redacted firewall ruleset,
positive and negative test output, timestamps, tool versions and hashes in the
evidence manifest. Promotion to `EFFECTIVE` additionally requires repeatable
operating evidence; this repository currently makes no such claim.
