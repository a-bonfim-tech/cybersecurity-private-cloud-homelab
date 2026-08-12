# Security Evidence Register

| ID | Classification | Type | Path | Description | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| PCAP-001 | TEST_VECTOR_SPECIFICATION | Packet capture | `docs/evidence/pcaps/recon_vlan30_to_vlan20.pcap` | One synthetic TCP SYN packet from VLAN 30 to VLAN 20; it does not prove a scan or firewall action. | File integrity and packet fields validated locally |
| LOG-001 | TEST_VECTOR_SPECIFICATION | JSON event | `docs/evidence/logs/wazuh_alerts_recon.json` | Hand-authored Suricata EVE input and expected Wazuh rule mapping. | JSON syntax validated; Wazuh execution pending |

The machine-readable source of truth is
[`evidence-manifest.json`](evidence-manifest.json). No item in this register is
currently classified as executed control-effectiveness evidence.
