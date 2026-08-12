# Trust Boundaries & Traffic Flow Matrix

## Network Zones
* VLAN 10 (TRUSTED): Admin Access
* VLAN 20 (SERVERS): Hosted Workloads (Bonfim AI Platform)
* VLAN 30 (CYBER LAB): Isolated Attack Testing
* VLAN 40 (MONITORING): Passive SPAN/TAP Sensors

## Inter-Zone Controls
Traffic between VLAN 20 and VLAN 10 is implicitly blocked by default-deny rules.
