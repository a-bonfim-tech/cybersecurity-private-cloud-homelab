# Cybersecurity Private Cloud Homelab

> **Enterprise-grade, Zero Trust Security Homelab & Detection Engineering Environment.**

- Architecture: Federated (docs/adr/ADR-001-federated-architecture.md)
- Security Model: Zero Trust (docs/governance/firewall-policy.md)
- Compliance: BSI / ISO27001 (docs/governance/bsi-iso-mapping.md)

---

## Executive Summary

This repository contains the architectural definition, declarative infrastructure-as-code (IaC), governance policies, detection engineering artifacts, compliance mappings, and evidence matrices of the **Cybersecurity Private Cloud Homelab**.

Designed under **Defense-in-Depth** and **Zero Trust** principles, the environment provides a segmented private cloud infrastructure (L2/L3 VLANs), monitored passively and actively by IDS/IPS sensors (Suricata) and SIEM (Wazuh). It serves as the secure hosting and monitoring layer for federated workloads, including the **[Bonfim AI Platform](https://github.com/a-bonfim-tech/bonfim-ai-platform)**.

---

## Key Artifacts & Portfolio Proofs

* **Architecture & ADRs:** [](docs/adr/ADR-001-federated-architecture.md) & [](docs/architecture/trust-boundaries.md)
* **Federated Integration:** [](docs/architecture/federated-integration.md)
* **Governance & Frameworks:** [](docs/governance/bsi-iso-mapping.md) & [](docs/governance/firewall-policy.md)
* **Detection Engineering:** [](detections/suricata/local.rules) & [](detections/wazuh/local_rules.xml)
* **Threat Modeling & Graphs:** [](attack-graphs/server-ingress-attack-graph.json) & [](docs/threat-model/threat-model.md)
* **Purple-Team Runbook:** [](docs/evidence/purple-team-runs/RUNBOOK-001-recon-and-pivoting.md)
* **Infrastructure-as-Code:** [](iac/terraform/main.tf)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
