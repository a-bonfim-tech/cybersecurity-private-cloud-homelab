# Reference Synthetic Firewall Policy Specification

## Scope and evidence boundary

This document defines `REFERENCE_SYNTHETIC_TOPOLOGY` and links its routed rules
to bounded execution in an isolated nftables reference harness.

It intentionally retains the historical `10/20/30/40` synthetic network model
used by the associated PCAP, Suricata, Wazuh and nftables evidence.

It is not the authoritative current native PF topology. The current policy is
defined in [`current-segmentation-policy.md`](current-segmentation-policy.md).

This document does not prove pfSense or Proxmox deployment or continuous
operating control effectiveness.

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
| FW-001 | VLAN 10 | VLAN 20 | TCP | 22 / SSH | ALLOW | Bounded server administration | Homelab administrator | Counter observed; kernel log not retained | None | Authorized admin source reaches synthetic listener | Port 23 reaches default deny | `FW-EXEC-001`, `FW-NEG-001` | TESTED_IN_REFERENCE_HARNESS |
| FW-002 | VLAN 20 | VLAN 40 | TCP | 1514 / Wazuh agent | ALLOW | Forward security telemetry | Homelab administrator | Counter observed; kernel log not retained | None | Synthetic connection reaches listener | Other destination port remains default denied | `FW-EXEC-002` | TESTED_IN_REFERENCE_HARNESS |
| FW-003 | VLAN 40 | VLAN 20 | L2 mirror | SPAN / TAP | ALLOW | Passive network observation | Homelab administrator | Sensor health | Physical or virtual mirror configuration | Sensor receives test packet | Sensor cannot initiate session to workload | Not exercised by routed harness | NOT_APPLICABLE_TO_ROUTED_REFERENCE_HARNESS |
| FW-004 | VLAN 30 | VLAN 20 | TCP | 22, 80, 443, 8080 | DENY | Isolate the authorized attack-simulation zone | Homelab administrator | Counter observed; kernel log not retained | Temporary test exception must be time-bound | Synthetic probes to 22 and 443 are denied | Explicit allow paths remain usable | `FW-EXEC-003`, `FW-EXEC-004` | TESTED_IN_REFERENCE_HARNESS |
| FW-005 | Any zone | Any other zone | Any | Any | DENY | Default-deny inter-zone baseline | Homelab administrator | Counter observed; kernel log not retained | Explicit rules above only | Two unlisted flows are denied | Explicit allows remain usable | `FW-EXEC-005`, `FW-EXEC-006`, `FW-NEG-001` | TESTED_IN_REFERENCE_HARNESS |

## Validation gate

`TESTED_IN_REFERENCE_HARNESS` requires a retained ruleset, positive and
negative test output, timestamps, tool versions and hashes in the evidence
manifest. The evidence under `docs/evidence/executions/firewall/` satisfies
that bounded reference gate for FW-001, FW-002, FW-004 and FW-005. Promotion to
`EFFECTIVE` additionally requires repeatable operating evidence; this
repository currently makes no such claim.

This is reference nftables enforcement evidence and does not prove pfSense or
Proxmox deployment.
