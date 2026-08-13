# Runbook 002: Peer-Trusted Network Persistence Gate

## Objective

Verify that the synthetic `peer-trusted` guest uses the approved VLAN 10 host
address without DHCP, a default route or DNS, and retains that state across a
controlled reboot.

## Preconditions and safety

1. Use only the authorized local UTM guest `peer-trusted`.
2. Preserve the current Netplan source before mutation.
3. Use the existing UTM console because applying network changes can interrupt
   remote management.
4. Enter privileged credentials locally; never record them in repository
   evidence.
5. Do not alter pfSense, another VM or a host-network object during this gate.

## Target state

| Property | Required value |
| :--- | :--- |
| Interface | `enp0s1` |
| IPv4 | `10.10.10.10/24` |
| DHCPv4 / DHCPv6 | disabled / disabled |
| Default route | absent |
| Interface DNS | absent |
| Persistent source | `/etc/netplan/01-segment2-client.yaml` |

## Validation procedure

1. Record the runtime address, route table and interface DNS state.
2. Inspect the persistent Netplan source.
3. Copy the source to a dated rollback path and verify its presence.
4. Write only the minimal target Netplan source.
5. Validate with `netplan generate` before applying.
6. Apply with `netplan apply` from the local console.
7. Recheck address, routes, DNS and persistent source.
8. Perform a controlled reboot.
9. Complete a human login using the existing local account.
10. Repeat all runtime and persistent checks and confirm the rollback file.

## Pass criteria

The gate passes only when generation and application succeed, immediate and
post-reboot runtime state match the target, the persistent source matches the
target, the rollback file remains present and a human can log in after reboot.

## Retained execution

The `2026-08-13` execution passed all criteria. Its minimized evidence is
retained under
[`../executions/peer-trusted-network/`](../executions/peer-trusted-network/).
The retained classification is `EXECUTED_SYNTHETIC_TEST_EVIDENCE`.

This result is not firewall-enforcement or operating-effectiveness evidence.
