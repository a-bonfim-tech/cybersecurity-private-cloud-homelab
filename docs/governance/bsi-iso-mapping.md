# Security Framework Alignment Mapping

## BSI IT-Grundschutz & ISO/IEC 27001 Alignment

This is a technical cross-reference, not a declaration of conformity,
certification or control effectiveness.

| Homelab control | BSI reference | ISO/IEC 27001:2022 reference | Repository artifact | Evidence state | Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Network segmentation | NET.1.1 Network Architecture | A.8.20 Network security | `firewall-policy.md` | DESIGNED | No applied firewall evidence |
| Centralized logging | OPS.1.1.5 Logging | A.8.15 Logging | Wazuh rules and test vector | SPECIFIED | No operating SIEM evidence |
| Intrusion detection | DER.1 Detection of Security-Relevant Events | A.8.16 Monitoring activities | Suricata local rule | CONFIGURED | Executed alert evidence pending |

The references must be checked against the controlled editions available to
the assessor before any formal assessment. The mappings express applicability
judgment only.

- `COMPLIANCE_CERTIFIED=false`
- `EXTERNAL_AUDIT_PERFORMED=false`
