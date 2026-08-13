# Asset Inventory & Classification

| Asset Name | Zone | IP Address | OS / Service | Criticality | Evidence state |
| :--- | :--- | :--- | :--- | :--- |
| `pfsense-core-fw` | Gateway / VLAN trunk | `10.10.10.1` (planned) | FreeBSD / pfSense | Critical | DESIGNED |
| `wazuh-manager-v40` | VLAN 40 | `10.10.40.10` (planned) | Ubuntu Server / Wazuh Manager | High | DESIGNED |
| `bonfim-ai-app-v20` | VLAN 20 | `10.10.20.15` (test vector) | Debian Linux / container workload | High | CONFIGURED_IN_TERRAFORM |
| `kali-lab-v30` | VLAN 30 | `10.10.30.5` (test vector) | Kali Linux / security test VM | Low (isolated) | SPECIFIED |

Addresses marked planned or test vector are not proof of deployed assets.
