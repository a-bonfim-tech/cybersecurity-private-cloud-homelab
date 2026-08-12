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
