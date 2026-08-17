# Trust Boundaries & Traffic Flow Matrix

## Topology classes

This repository intentionally retains two network models.

### CURRENT_NATIVE_PF_TOPOLOGY

This is the authoritative current lab segmentation model.

| Zone | CIDR | Router interface |
| :--- | :--- | :--- |
| USERS | `10.10.10.0/27` | `vtnet1` |
| SERVERS | `10.10.20.0/24` | `vtnet2` |
| MONITORING | `10.10.60.0/25` | `vtnet3` |
| MANAGEMENT | `10.10.70.0/28` | `vtnet4` |

Native FreeBSD PF execution evidence is retained as
[`FBSD-PF-SEG-EXEC-001`](../evidence/executions/freebsd-pf-segmentation/README.md).

The bounded execution demonstrated routing, NAT, selected inter-zone allow and
deny paths, management access and controlled reboot persistence.

### REFERENCE_SYNTHETIC_TOPOLOGY

Historical detection engineering and the nftables reference harness use:

| Zone | CIDR |
| :--- | :--- |
| TRUSTED | `10.10.10.0/24` |
| SERVERS | `10.10.20.0/24` |
| CYBER LAB | `10.10.30.0/24` |
| MONITORING | `10.10.40.0/24` |

This model remains valid for its retained PCAP, Suricata, Wazuh and nftables
test evidence. It is not the authoritative current native PF topology.

## Inter-zone controls

The current native PF baseline is default deny with explicit permitted paths.

Observed bounded paths include:

| Source | Destination | Observed result |
| :--- | :--- | :--- |
| MONITORING | USERS | ALLOW |
| MONITORING | SERVERS | ALLOW |
| MONITORING | MANAGEMENT | DENY |
| MANAGEMENT | USERS | ALLOW |
| MANAGEMENT | SERVERS | ALLOW |
| MANAGEMENT | MONITORING | ALLOW |
| USERS | SERVERS | DENY |

These observations are bounded lab evidence and do not establish continuous
operating effectiveness.

## Historical peer-trusted evidence

`PEER-TRUSTED-NET-EXEC-001` is retained guest-configuration evidence. The
historical package contains both `/27` and `/24` address states across its
correction procedure.

It therefore MUST NOT be used as the source of truth for the current network
prefix. The authoritative current USERS network is `10.10.10.0/27`, supported
by the native PF execution evidence.

See
[`ADR-002`](../adr/ADR-002-topology-reconciliation.md)
for the topology reconciliation decision.
