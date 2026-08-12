# Cybersecurity Private Cloud Homelab

> **Enterprise-grade, Zero Trust Security Homelab & Detection Engineering Environment.**

- Architecture: Federated (docs/adr/ADR-001-federated-architecture.md)
- Security Model: Zero Trust (docs/governance/firewall-policy.md)
- Compliance: BSI / ISO27001 (docs/governance/bsi-iso-mapping.md)

<p align="center">
  <img src="docs/architecture/hero-architecture.png" alt="Zero Trust Architecture Core & Attack Graph Engine" width="100%" />
</p>

---

## Executive Summary

This repository contains the architectural definition, declarative infrastructure-as-code (IaC), governance policies, detection engineering artifacts, compliance mappings, and evidence matrices of the **Cybersecurity Private Cloud Homelab**.

Designed under **Defense-in-Depth** and **Zero Trust** principles, the environment provides a segmented private cloud infrastructure (L2/L3 VLANs), monitored passively and actively by IDS/IPS sensors (Suricata) and SIEM (Wazuh). It serves as the secure hosting and monitoring layer for federated workloads, including the **[Bonfim AI Platform](https://github.com/a-bonfim-tech/bonfim-ai-platform)**.

---

## Key Artifacts & Portfolio Proofs

* **Architecture & ADRs:** [`ADR-001`](docs/adr/ADR-001-federated-architecture.md) & [`trust-boundaries.md`](docs/architecture/trust-boundaries.md)
* **Federated Integration:** [`federated-integration.md`](docs/architecture/federated-integration.md)
* **Governance & Frameworks:** [`bsi-iso-mapping.md`](docs/governance/bsi-iso-mapping.md) & [`firewall-policy.md`](docs/governance/firewall-policy.md)
* **Detection Engineering:** [`local.rules`](detections/suricata/local.rules) & [`local_rules.xml`](detections/wazuh/local_rules.xml)
* **Threat Modeling & Graphs:** [`server-ingress-attack-graph.json`](attack-graphs/server-ingress-attack-graph.json) & [`threat-model.md`](docs/threat-model/threat-model.md)
* **Purple-Team Runbook:** [`RUNBOOK-001`](docs/evidence/purple-team-runs/RUNBOOK-001-recon-and-pivoting.md)
* **Infrastructure-as-Code:** [`main.tf`](iac/terraform/main.tf)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
