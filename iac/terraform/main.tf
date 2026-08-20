terraform {
  required_version = ">= 1.5.0, < 2.0.0"
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "3.0.1-rc1"
    }
  }
}

# Target network assignments are aligned to CURRENT_NATIVE_PF_TOPOLOGY.
# The gateway VM remains a pfSense target configuration and is distinct from
# the executed FreeBSD PF lab router. This repository contains no evidence of
# terraform apply.
provider "proxmox" {
  pm_api_url          = var.proxmox_api_url
  pm_api_token_id     = var.proxmox_api_token_id
  pm_api_token_secret = var.proxmox_api_token_secret
  pm_tls_insecure     = var.proxmox_tls_insecure
}

variable "proxmox_api_url" {
  type        = string
  description = "Proxmox VE API endpoint on the restricted management network."

  validation {
    condition = (
      can(regex(
        "^https://10\\.10\\.70\\.([1-9]|1[0-4]):8006/api2/json$",
        var.proxmox_api_url,
      ))
    )
    error_message = "The Proxmox API URL must use HTTPS and an address in the 10.10.70.0/28 management network."
  }
}

variable "proxmox_api_token_id" {
  type        = string
  description = "Proxmox API token identifier supplied outside version control."
  sensitive   = true
}

variable "proxmox_api_token_secret" {
  type        = string
  description = "Proxmox API token secret supplied outside version control."
  sensitive   = true
}

variable "proxmox_tls_insecure" {
  type        = bool
  default     = false
  description = "Permit an untrusted Proxmox TLS certificate in an isolated lab only."
}

variable "target_node" {
  type        = string
  default     = "pve-node-01"
  description = "Proxmox Host Node"

  validation {
    condition     = length(trimspace(var.target_node)) > 0
    error_message = "The target node must not be empty."
  }
}

resource "proxmox_vm_qemu" "pfsense_gateway" {
  name        = "pfsense-core-fw"
  target_node = var.target_node
  vmid        = 100
  cores       = 2
  memory      = 2048

  network {
    model  = "virtio"
    bridge = "vmbr0"
    tag    = 10
  }

  network {
    model  = "virtio"
    bridge = "vmbr0"
    tag    = 20
  }

  network {
    model  = "virtio"
    bridge = "vmbr0"
    tag    = 60
  }

  network {
    model  = "virtio"
    bridge = "vmbr0"
    tag    = 70
  }
}

resource "proxmox_vm_qemu" "bonfim_ai_workload" {
  name        = "bonfim-ai-app-v20"
  target_node = var.target_node
  vmid        = 201
  cores       = 4
  memory      = 8192

  network {
    model  = "virtio"
    bridge = "vmbr0"
    tag    = 20
  }
}

output "gateway_vlan_assignments" {
  description = "Target Proxmox VLAN assignments aligned to CURRENT_NATIVE_PF_TOPOLOGY. Configuration only; terraform apply is not evidenced."
  value = {
    users      = "VLAN 10 - 10.10.10.0/27"
    servers    = "VLAN 20 - 10.10.20.0/24"
    monitoring = "VLAN 60 - 10.10.60.0/25"
    management = "VLAN 70 - 10.10.70.0/28"
  }
}
