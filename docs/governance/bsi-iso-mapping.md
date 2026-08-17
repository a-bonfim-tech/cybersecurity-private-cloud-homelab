# Security Framework Alignment Mapping

## BSI IT-Grundschutz & ISO/IEC 27001 Alignment

This is a technical cross-reference, not a declaration of conformity,
certification or control effectiveness.

| Homelab control | BSI reference | ISO/IEC 27001:2022 reference | Repository artifact | Evidence state | Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Network segmentation | NET.1.1 Network Architecture | A.8.20 Network security | `current-segmentation-policy.md`, `firewall-policy.md`, `FBSD-PF-SEG-EXEC-001` and reference nftables evidence | NATIVE_PF_AND_REFERENCE_HARNESS_TESTED | Native FreeBSD PF segmentation is bounded execution evidence; historical nftables remains reference-policy evidence. No pfSense deployment, certification or continuous operating-effectiveness claim. |
| Centralized logging | OPS.1.1.5 Logging | A.8.15 Logging | Wazuh rules and native logtest evidence | TESTED_WITH_WAZUH_LOGTEST | Decoder and rule evaluation only; no operating manager ingestion or persistence evidence |
| Intrusion detection | DER.1 Detection of Security-Relevant Events | A.8.16 Monitoring activities | Suricata local rule and offline replay evidence | TESTED_OFFLINE | Synthetic PCAP replay only; no live network IDS or operating-effectiveness evidence |

The references must be checked against the controlled editions available to
the assessor before any formal assessment. The mappings express applicability
judgment only.

- `COMPLIANCE_CERTIFIED=false`
- `EXTERNAL_AUDIT_PERFORMED=false`
