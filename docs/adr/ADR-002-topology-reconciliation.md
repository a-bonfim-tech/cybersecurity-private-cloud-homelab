# ADR-002: Validated Topology Reconciliation

* Status: Accepted
* Date: 2026-08-17
* Decider: Andre Bonfim

## Context

The repository contains two legitimate but different network models.

The historical synthetic detection and nftables reference harness uses:

| Zone | Network |
| :--- | :--- |
| TRUSTED | `10.10.10.0/24` |
| SERVERS | `10.10.20.0/24` |
| CYBER LAB | `10.10.30.0/24` |
| MONITORING | `10.10.40.0/24` |

A later native FreeBSD PF execution validated a different four-zone topology:

| Zone | Network | Router interface |
| :--- | :--- | :--- |
| USERS | `10.10.10.0/27` | `vtnet1` |
| SERVERS | `10.10.20.0/24` | `vtnet2` |
| MONITORING | `10.10.60.0/25` | `vtnet3` |
| MANAGEMENT | `10.10.70.0/28` | `vtnet4` |

Treating both models as one topology creates ambiguity between historical test
vectors, current architecture and future infrastructure configuration.

## Decision

The native FreeBSD PF topology is the authoritative current lab segmentation
model and the target topology for current infrastructure-as-code.

The `10.10.10.0/24`, `10.10.20.0/24`, `10.10.30.0/24`,
`10.10.40.0/24` model is retained as `REFERENCE_SYNTHETIC_TOPOLOGY`.

Historical PCAPs, Suricata outputs, Wazuh outputs, nftables rulesets and their
associated retained evidence MUST NOT be silently rewritten to the current
native topology.

Current architecture documents and target IaC use
`CURRENT_NATIVE_PF_TOPOLOGY`.

IaC alignment in this decision concerns the zone, VLAN and CIDR model. The
Terraform gateway resource remains a configured pfSense VM target and has not
been applied. Native FreeBSD PF execution and the unexecuted pfSense IaC target
are therefore distinct implementation classes and MUST NOT be presented as the
same deployed gateway.

## Evidence boundary

`FBSD-PF-SEG-EXEC-001` is the retained execution evidence for the current
native PF topology.

Historical Suricata, Wazuh and nftables executions remain valid only inside
their explicitly bounded reference topology.

`PEER-TRUSTED-NET-EXEC-001` is historical guest-configuration evidence. Its
retained package includes both `/27` and `/24` address states and therefore is
not an authoritative source for the current network prefix.

No decision in this ADR proves Proxmox deployment, Terraform apply, pfSense
execution, compliance certification or continuous operating effectiveness.

## Consequences

Architecture and IaC become consistent with the native PF execution.

Historical test evidence remains reproducible and attributable to the exact
network model under which it was generated.

Future end-to-end detection evidence should use the current native topology or
declare an explicit topology class.
