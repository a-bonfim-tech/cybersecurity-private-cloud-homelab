# Current Native PF Segmentation Policy

## Scope

This document describes `CURRENT_NATIVE_PF_TOPOLOGY`.

The policy is supported by bounded native FreeBSD PF execution retained as
`FBSD-PF-SEG-EXEC-001`.

It does not claim continuous operating effectiveness, pfSense execution,
Proxmox deployment or compliance certification.

## Current zones

| Zone | CIDR | Gateway | Interface |
| :--- | :--- | :--- | :--- |
| USERS | `10.10.10.0/27` | `10.10.10.1` | `vtnet1` |
| SERVERS | `10.10.20.0/24` | `10.10.20.1` | `vtnet2` |
| MONITORING | `10.10.60.0/25` | `10.10.60.1` | `vtnet3` |
| MANAGEMENT | `10.10.70.0/28` | `10.10.70.1` | `vtnet4` |

## Policy invariants

1. Inter-zone traffic is denied unless explicitly permitted.
2. MONITORING may reach USERS and SERVERS.
3. MONITORING must not initiate access to MANAGEMENT.
4. MANAGEMENT may administer internal segments.
5. USERS must not initiate access to SERVERS under the validated baseline.
6. All four current internal networks may use outbound NAT.
7. Management SSH to the router is an explicitly validated administrative path.

## Retained native execution matrix

| Source | Destination | Protocol | Expected | Observed |
| :--- | :--- | :--- | :--- | :--- |
| MONITORING | USERS | ICMP | ALLOW | PASS |
| MONITORING | SERVERS | ICMP | ALLOW | PASS |
| MONITORING | SERVERS | TCP/22 | ALLOW | PASS |
| MONITORING | MANAGEMENT | ICMP | DENY | BLOCK |
| MANAGEMENT | USERS | ICMP | ALLOW | PASS |
| MANAGEMENT | SERVERS | ICMP | ALLOW | PASS |
| MANAGEMENT | MONITORING | ICMP | ALLOW | PASS |
| USERS | SERVERS | ICMP | DENY | BLOCK |
| USERS | SERVERS | TCP/22 | DENY | BLOCK |
| MONITORING | Internet | ICMP/NAT | ALLOW | PASS |
| MANAGEMENT | Router | TCP/22 | ALLOW | PASS |

Evidence:
[`docs/evidence/executions/freebsd-pf-segmentation/`](../evidence/executions/freebsd-pf-segmentation/)

## Reference-policy relationship

The older
[`firewall-policy.md`](firewall-policy.md)
describes `REFERENCE_SYNTHETIC_TOPOLOGY` and remains associated with the
historical nftables execution evidence.

Its VLAN 30 and VLAN 40 rules are not silently mapped onto the current native
PF topology.
