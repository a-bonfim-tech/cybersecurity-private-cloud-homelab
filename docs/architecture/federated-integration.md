# Federated Integration: Bonfim AI Platform & Security Homelab

## Architecture Overview

The Bonfim AI Platform operates as a hosted workload inside VLAN 20 (SERVERS zone).

## Integration Points
1. **Ingress Control:** Inbound traffic routed via WAF/Reverse Proxy (DMZ) to AI Platform API endpoints.
2. **Telemetry Forwarding:** Wazuh Agent on AI Platform host streams logs to SIEM Manager (VLAN 40).
3. **Network Isolation:** Direct connection from AI Platform to Management Zone (VLAN 10) is blocked by default.
