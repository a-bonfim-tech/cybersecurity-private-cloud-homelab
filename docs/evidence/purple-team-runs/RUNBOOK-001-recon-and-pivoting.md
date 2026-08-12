# Purple-Team Runbook 001: Reconnaissance & Pivoting Simulation

## Objective
Validate Suricata IDS rule (SID: 1000001) and Wazuh SSH alert when an unauthorized internal scan originates from VLAN 30 (Cyber Lab) towards VLAN 20 (Servers).

## Attack Execution


## Telemetry & Detection Verification
1. **Suricata Alert:**  generated in .
2. **Wazuh SIEM Alert:** Level 7 alert triggered for unauthorized port probe.
3. **Firewall Action:** Packet dropped by default-deny rule between VLAN 30 and VLAN 20.
