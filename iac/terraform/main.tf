terraform {
  required_version = ">= 1.5.0, < 2.0.0"
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "3.0.1-rc1"
    }
  }
}

# Configuration only: this repository contains no evidence of terraform apply.
provider "proxmox" {
  pm_api_url          = var.proxmox_api_url
  pm_api_token_id     = var.proxmox_api_token_id
  pm_api_token_secret = var.proxmox_api_token_secret
  pm_tls_insecure     = var.proxmox_tls_insecure
}

variable "proxmox_api_url" {
  type        = string
  default     = "https://10.10.10.2:8006/api2/json"
  description = "Proxmox VE API Endpoint"

  validation {
    condition     = can(regex("^https://", var.proxmox_api_url))
    error_message = "The Proxmox API URL must use HTTPS."
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
    tag    = 30
  }

  network {
    model  = "virtio"
    bridge = "vmbr0"
    tag    = 40
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
  value = {
    trusted    = "VLAN 10 - 10.10.10.0/24"
    servers    = "VLAN 20 - 10.10.20.0/24"
    cyberlab   = "VLAN 30 - 10.10.30.0/24"
    monitoring = "VLAN 40 - 10.10.40.0/24"
  }
}
