# Security Evidence Register

| ID | Classification | Type | Path | Description | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| PCAP-001 | TEST_VECTOR_SPECIFICATION | Packet capture | `docs/evidence/pcaps/recon_vlan30_to_vlan20.pcap` | One synthetic TCP SYN packet from VLAN 30 to VLAN 20; it does not prove a scan or firewall action. | File integrity and packet fields validated locally |
| LOG-001 | TEST_VECTOR_SPECIFICATION | JSON event | `docs/evidence/logs/wazuh_alerts_recon.json` | Hand-authored Suricata EVE input and expected Wazuh rule mapping. | JSON syntax validated; this hand-authored vector is not execution evidence |
| PCAP-POS-001 | TEST_VECTOR_SPECIFICATION | Packet capture | `docs/evidence/pcaps/recon_vlan30_to_vlan20_positive_scan.pcap` | Nine deterministic SYN packets that cross the Suricata threshold. | Generation and packet fields validated |
| PCAP-NEG-001 | TEST_VECTOR_SPECIFICATION | Packet capture | `docs/evidence/pcaps/recon_vlan30_to_vlan20_negative_below_threshold.pcap` | Seven deterministic SYN packets below the threshold. | Generation and packet fields validated |
| PCAP-NEG-002 | TEST_VECTOR_SPECIFICATION | Packet capture | `docs/evidence/pcaps/recon_vlan30_to_vlan20_negative_ack.pcap` | Eight deterministic ACK packets outside the SYN rule. | Generation and packet fields validated |
| SURICATA-EXEC-001 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Offline rule execution | `docs/evidence/executions/suricata/` | Suricata 8.0.6 configuration, positive replay and two negative controls. | One positive SID 1000001 alert; zero negative alerts |
| WAZUH-EXEC-001 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Native rule test | `docs/evidence/executions/wazuh/` | Actual Suricata alert decoded and evaluated by Wazuh 4.14.7. | Rule 100010 level 7 and T1046 matched |
| WAZUH-NEG-001 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Native negative test | `docs/evidence/executions/wazuh/` | Different signature ID. | Rule 100010 did not match |
| WAZUH-NEG-002 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Native negative test | `docs/evidence/executions/wazuh/` | Non-alert event type. | Rule 100010 did not match |
| FW-EXEC-001 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Reference policy enforcement | `docs/evidence/executions/firewall/` | TRUSTED-to-SERVERS SSH allow in the isolated nftables harness. | `implementation_class=REFERENCE_POLICY_ENFORCEMENT`; connection and FW-001 counter passed |
| FW-EXEC-002 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Reference policy enforcement | `docs/evidence/executions/firewall/` | SERVERS-to-MONITORING TCP/1514 allow in the isolated nftables harness. | `implementation_class=REFERENCE_POLICY_ENFORCEMENT`; connection and FW-002 counter passed |
| FW-EXEC-003 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Reference policy enforcement | `docs/evidence/executions/firewall/` | CYBER_LAB-to-SERVERS SSH explicit deny in the isolated nftables harness. | `implementation_class=REFERENCE_POLICY_ENFORCEMENT`; denial and FW-004 counter passed |
| FW-EXEC-004 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Reference policy enforcement | `docs/evidence/executions/firewall/` | CYBER_LAB-to-SERVERS HTTPS explicit deny in the isolated nftables harness. | `implementation_class=REFERENCE_POLICY_ENFORCEMENT`; denial and FW-004 counter passed |
| FW-EXEC-005 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Reference policy enforcement | `docs/evidence/executions/firewall/` | TRUSTED-to-MONITORING unlisted-port default deny in the isolated nftables harness. | `implementation_class=REFERENCE_POLICY_ENFORCEMENT`; denial and FW-005 counter passed |
| FW-EXEC-006 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Reference policy enforcement | `docs/evidence/executions/firewall/` | SERVERS-to-TRUSTED unlisted-port default deny in the isolated nftables harness. | `implementation_class=REFERENCE_POLICY_ENFORCEMENT`; denial and FW-005 counter passed |
| FW-NEG-001 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Reference negative test | `docs/evidence/executions/firewall/` | TRUSTED-to-SERVERS TCP/23 verifies allow-rule port scoping. | `implementation_class=REFERENCE_POLICY_ENFORCEMENT`; denial and FW-005 counter passed |
| PEER-TRUSTED-NET-EXEC-001 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Historical guest network persistence | `docs/evidence/executions/peer-trusted-network/` | Historical correction and reboot evidence; retained package contains both `/27` and `/24` states and is not authoritative for current topology. | Bounded guest procedure retained; current prefix authority is `FBSD-PF-SEG-EXEC-001` |
| FBSD-PF-SEG-EXEC-001 | EXECUTED_SYNTHETIC_TEST_EVIDENCE | Native FreeBSD PF segmentation | `docs/evidence/executions/freebsd-pf-segmentation/` | Observed native PF routing, NAT, inter-zone allow/deny behavior and controlled reboot persistence in the local UTM lab. | `implementation_class=NATIVE_FREEBSD_PF_SEGMENTATION`; allow/deny matrix, NAT, PF reload and post-reboot management path validated |

The machine-readable source of truth is
[`evidence-manifest.json`](evidence-manifest.json). No item in this register is
classified as operating control-effectiveness evidence. The peer-trusted item
is guest-configuration evidence, not pfSense or inter-zone enforcement
evidence. The firewall items are reference nftables policy-enforcement
evidence, not native pfSense enforcement.
