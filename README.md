# Cybersecurity Private Cloud Homelab

> Evidence-oriented design for a segmented private-cloud security lab and its
> synthetic detection-engineering scenarios.

- Architecture: [federated design](docs/adr/ADR-001-federated-architecture.md)
- Security model: [default-deny policy specification](docs/governance/firewall-policy.md)
- Governance: [BSI and ISO/IEC control mapping](docs/governance/bsi-iso-mapping.md)

---

## Executive Summary

This repository contains the architectural definition, declarative
infrastructure-as-code (IaC), governance policies, detection artifacts and
evidence specifications for the **Cybersecurity Private Cloud Homelab**.

The design applies defense-in-depth and Zero Trust principles to four proposed
L2/L3 VLANs. Terraform resources and detection rules are **configured** and
syntax-validated where the required tooling is available. The repository does
not yet demonstrate an applied Proxmox deployment, an enforced firewall policy,
or operating control effectiveness. It is intended to host federated workloads,
including the **[Bonfim AI Platform](https://github.com/a-bonfim-tech/bonfim-ai-platform)**.

## Evidence Status

| Capability | Current state | Evidence boundary |
| :--- | :--- | :--- |
| Network segmentation | DESIGNED | VLANs and flows are specified; enforcement is not observed here. |
| Proxmox infrastructure | CONFIGURED | Terraform is present; no `terraform apply` evidence is claimed. |
| Suricata reconnaissance detection | CONFIGURED | Rule and synthetic PCAP specification exist; executed alert evidence is pending. |
| Wazuh correlation | SPECIFIED | Rules and test vectors are not operating evidence. |
| BSI / ISO/IEC alignment | MAPPED | Mapping is not certification or formal compliance. |

- `COMPLIANCE_CERTIFIED=false`
- `EXTERNAL_AUDIT_PERFORMED=false`

---

## Key Artifacts & Portfolio Proofs

* **Architecture & ADRs:** [`ADR-001`](docs/adr/ADR-001-federated-architecture.md) & [`trust-boundaries.md`](docs/architecture/trust-boundaries.md)
* **Federated Integration:** [`federated-integration.md`](docs/architecture/federated-integration.md)
* **Governance & Framework Mapping:** [`bsi-iso-mapping.md`](docs/governance/bsi-iso-mapping.md) & [`firewall-policy.md`](docs/governance/firewall-policy.md)
* **Detection Engineering:** [`local.rules`](detections/suricata/local.rules) & [`local_rules.xml`](detections/wazuh/local_rules.xml)
* **Threat Modeling & Graphs:** [`server-ingress-attack-graph.json`](attack-graphs/server-ingress-attack-graph.json) & [`threat-model.md`](docs/threat-model/threat-model.md)
* **Purple-Team Runbook:** [`RUNBOOK-001`](docs/evidence/purple-team-runs/RUNBOOK-001-recon-and-pivoting.md)
* **Evidence Manifest:** [`evidence-manifest.json`](docs/evidence/evidence-manifest.json)
* **Infrastructure-as-Code:** [`main.tf`](iac/terraform/main.tf)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
