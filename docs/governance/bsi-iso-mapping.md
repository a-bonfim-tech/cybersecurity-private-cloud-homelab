# Security Framework Compliance Mapping

## BSI IT-Grundschutz & ISO/IEC 27001 Alignment

| Homelab Control | BSI Module | ISO 27001:2022 Control | Implementation |
| :--- | :--- | :--- | :--- |
| Network Segmentation | NET.1.1 Network Architecture | A.8.20 Network Security | 802.1Q VLANs & Default-Deny Firewall Rules |
| Centralized Logging | OPS.1.1.5 Logging & Monitoring | A.8.15 Logging | Wazuh SIEM & SPAN Traffic Mirroring |
| Intrusion Detection | DER.1 Detection of Security Incidents | A.8.16 Monitoring Activities | Suricata IDS with Custom Rules |
