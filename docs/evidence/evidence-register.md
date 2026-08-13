# Security Evidence Register

| ID | Classification | Type | Path | Description | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| PCAP-001 | TEST_VECTOR_SPECIFICATION | Packet capture | `docs/evidence/pcaps/recon_vlan30_to_vlan20.pcap` | One synthetic TCP SYN packet from VLAN 30 to VLAN 20; it does not prove a scan or firewall action. | File integrity and packet fields validated locally |
| LOG-001 | TEST_VECTOR_SPECIFICATION | JSON event | `docs/evidence/logs/wazuh_alerts_recon.json` | Hand-authored Suricata EVE input and expected Wazuh rule mapping. | JSON syntax validated; Wazuh execution pending |
| PCAP-POS-001 | TEST_VECTOR_SPECIFICATION | Packet capture | `docs/evidence/pcaps/recon_vlan30_to_vlan20_positive_scan.pcap` | Nine deterministic SYN packets that cross the Suricata threshold. | Generation and packet fields validated |
| PCAP-NEG-001 | TEST_VECTOR_SPECIFICATION | Packet capture | `docs/evidence/pcaps/recon_vlan30_to_vlan20_negative_below_threshold.pcap` | Seven deterministic SYN packets below the threshold. | Generation and packet fields validated |
| PCAP-NEG-002 | TEST_VECTOR_SPECIFICATION | Packet capture | `docs/evidence/pcaps/recon_vlan30_to_vlan20_negative_ack.pcap` | Eight deterministic ACK packets outside the SYN rule. | Generation and packet fields validated |
| SURICATA-EXEC-001 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Offline rule execution | `docs/evidence/executions/suricata/` | Suricata 8.0.6 configuration, positive replay and two negative controls. | One positive SID 1000001 alert; zero negative alerts |

The machine-readable source of truth is
[`evidence-manifest.json`](evidence-manifest.json). No item in this register is
classified as firewall or operating control-effectiveness evidence.
