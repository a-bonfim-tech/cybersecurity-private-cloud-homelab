# Recruiter Brief

## 1. Executive summary

This repository is an evidence-oriented private-cloud security lab combining
network segmentation, infrastructure as code, detection engineering,
governance documentation and versioned macOS security research. It demonstrates
how security claims can be implemented, tested and bounded by retained
evidence without presenting a laboratory result as production assurance.

## 2. Architecture snapshot

The current native lab uses a FreeBSD PF router and four security zones:
Users, Servers, Monitoring and Management. A separate historical synthetic
topology supports reproducible nftables, Suricata and Wazuh tests. Terraform
defines a Proxmox/pfSense target configuration but has not been applied.

Key architecture sources:

- [topology reconciliation](adr/ADR-002-topology-reconciliation.md)
- [trust boundaries](architecture/trust-boundaries.md)
- [current segmentation policy](governance/current-segmentation-policy.md)

## 3. Security capabilities demonstrated

- default-deny network policy and explicit inter-zone paths;
- native PF routing, NAT and reboot-persistence validation;
- deterministic Suricata positive and negative controls;
- native Wazuh rule evaluation for retained rule `100010` evidence;
- threat modeling, ADRs and BSI/ISO control mapping;
- privacy-aware evidence acquisition and integrity validation;
- least-privilege CI and digest- or commit-pinned dependencies where retained.

## 4. Evidence-backed results

| Capability | State | Evidence boundary |
|---|---|---|
| FreeBSD PF segmentation | `EVIDENCED` | Bounded native lab matrix, routing, NAT and controlled reboot |
| nftables reference policy | `EVIDENCED` | Isolated synthetic four-zone harness |
| Suricata reconnaissance rule | `TESTED` | One positive and two bounded negative PCAP controls |
| Wazuh rule `100010` | `TESTED` | Native `wazuh-logtest`; no manager-ingestion claim |
| Proxmox/pfSense IaC | `IMPLEMENTED` and statically validated | No apply or runtime evidence |
| Camera provider behavior | `SUPPORTED` on one host | Same-host provider-level repeatability |
| QuickTime versus Photo Booth | `PROVIDER_ONLY` | Valid provider contrast; no direct client discriminator |

The canonical inventory is the [evidence register](evidence/evidence-register.md).

## 5. What was not demonstrated

- Proxmox deployment or `terraform apply`;
- pfSense execution;
- a continuous PF-to-Suricata-to-Wazuh packet path;
- production readiness, compliance certification or control effectiveness;
- cross-host camera replication;
- client-level camera attribution or direct frame delivery.

## 6. Key engineering decisions

- Current and historical topologies remain explicitly separated.
- Historical evidence, negative results and aborted executions are retained.
- Protocol and runner tags freeze research methods before interpretation.
- Raw workstation evidence stays private; public artifacts are minimized.
- Management-plane configuration is restricted to the Management subnet.
- Second-host replication uses a disposable worktree rather than mutating the
  operator's active checkout.

## 7. Testing and validation

The repository validates Terraform formatting/configuration, JSON, XML, shell
syntax, deterministic PCAP generation, evidence hashes, Suricata behavior and
61 macOS research unit tests. CI executes the non-privileged reproducible
subset. Capability-dependent Docker and native-host tests are reported
separately from static validation.

## 8. Research rigor

The camera research distinguishes `OBSERVED`, `SUPPORTED`, `INFERRED`,
`HYPOTHESIS`, `UNSUPPORTED` and `NOT_TESTED`. The final client-discrimination
classification is `PROVIDER_ONLY`:

> Provider stream-related activity only; not direct frame-delivery evidence.

See the [experiment register](../research/macos-camera-attribution/docs/experiment-register.md)
and [findings](../research/macos-camera-attribution/docs/findings.md).

## 9. Relevant roles

The evidence is most relevant to Security Engineer, Detection Engineer,
Platform Security Engineer and Cybersecurity Researcher positions. It shows
strong junior-to-mid-level implementation depth with selected senior-level
behaviors in evidence discipline, claim calibration and research integrity.

## 10. Repository map

| Path | Primary value |
|---|---|
| `docs/architecture`, `docs/adr` | Architecture and decision traceability |
| `docs/evidence` | Retained evidence, hashes and execution boundaries |
| `detections` | Suricata and Wazuh rules |
| `iac/terraform` | Proxmox/pfSense target configuration |
| `tools` | Validation and isolated test harnesses |
| `research/macos-camera-attribution` | Versioned research, tests and conclusions |

Start with the root [README](../README.md), then inspect only the evidence or
implementation relevant to the role being evaluated.
