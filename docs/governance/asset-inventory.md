# Security Asset Inventory

## Current and target assets

| Asset | Role / zone | Address or placement | Technology | Criticality | Evidence state |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `s2-freebsd-router` | Current native security gateway | `10.10.10.1`, `10.10.20.1`, `10.10.60.1`, `10.10.70.1` | FreeBSD 14.3 / PF | Critical | EXECUTED_SYNTHETIC_TEST_EVIDENCE |
| `bonfim-ai-app-v20` | SERVERS workload target | VLAN 20 | Proxmox VM target / application workload | High | CONFIGURED_IN_TERRAFORM |
| `pfsense-core-fw` | Alternative Proxmox gateway target | VLAN 10/20/60/70 attachment model | pfSense VM target | Critical | CONFIGURED_IN_TERRAFORM_NOT_APPLIED |

## Historical reference-test assets

The following belong to `REFERENCE_SYNTHETIC_TOPOLOGY` and are not current
native PF assets.

| Asset | Reference zone | Address | Purpose | Evidence state |
| :--- | :--- | :--- | :--- | :--- |
| `kali-lab-v30` | CYBER LAB | `10.10.30.5` | Synthetic reconnaissance source | TEST_VECTOR_AND_EXECUTION_REFERENCE |
| `wazuh-manager-v40` | MONITORING | `10.10.40.10` | Synthetic/reference telemetry destination | REFERENCE_CONFIGURATION |
| `bonfim-ai-app-v20` test vector | SERVERS | `10.10.20.15` | Controlled server target | TEST_VECTOR |

## Interpretation

`FBSD-PF-SEG-EXEC-001` is the authority for the current native PF network
topology.

Terraform configuration does not prove that `pfsense-core-fw`,
`bonfim-ai-app-v20` or any Proxmox resource was applied.

Historical test-vector addresses remain retained because changing them would
invalidate the relationship between the original test inputs and their
execution evidence.
