# Federated Integration

## Architecture boundary

The Bonfim AI Platform is modeled as a workload in the SERVERS zone of
`CURRENT_NATIVE_PF_TOPOLOGY`.

Current network zones are:

| Zone | CIDR |
| :--- | :--- |
| USERS | `10.10.10.0/27` |
| SERVERS | `10.10.20.0/24` |
| MONITORING | `10.10.60.0/25` |
| MANAGEMENT | `10.10.70.0/28` |

## Integration model

1. **Workload placement:** Bonfim AI Platform remains associated with the
   SERVERS zone.
2. **Telemetry:** security telemetry is intended to flow toward services in
   MONITORING. Operational Wazuh-manager deployment on the current topology is
   not proven.
3. **Administration:** administrative access originates from MANAGEMENT where
   explicitly permitted.
4. **Isolation:** ordinary USERS traffic does not receive implicit access to
   SERVERS.
5. **Federation:** application and security infrastructure remain independently
   versioned repositories with explicit integration boundaries.

## Evidence boundary

Native FreeBSD PF evidence validates selected network paths in the current
topology but does not prove deployment of Bonfim AI Platform, Wazuh Manager,
pfSense or Proxmox.

Historical VLAN 30 and VLAN 40 Suricata, Wazuh and nftables evidence belongs to
`REFERENCE_SYNTHETIC_TOPOLOGY` and is intentionally not rewritten.

See
[`ADR-002`](../adr/ADR-002-topology-reconciliation.md).
