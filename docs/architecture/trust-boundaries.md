# Trust Boundaries & Traffic Flow Matrix

## Network Zones
* VLAN 10 (TRUSTED): Admin Access
* VLAN 20 (SERVERS): Hosted Workloads (Bonfim AI Platform)
* VLAN 30 (CYBER LAB): Isolated Attack Testing
* VLAN 40 (MONITORING): Passive SPAN/TAP Sensors

## Inter-Zone Controls

The intended control is explicit allowlisting over a default-deny inter-zone
baseline. The complete designed matrix is maintained in
[`firewall-policy.md`](../governance/firewall-policy.md). Enforcement has not
been observed or demonstrated by this repository.

## Executed guest-network gate

The synthetic VLAN 10 `peer-trusted` guest was validated with persistent and
post-reboot runtime address `10.10.10.10/24`, no default route and no
interface-scoped DNS. Evidence is retained as
[`PEER-TRUSTED-NET-EXEC-001`](../evidence/executions/peer-trusted-network/).

This proves one guest's configuration persistence only. It does not change the
inter-zone enforcement boundary above and does not prove pfSense behavior.
