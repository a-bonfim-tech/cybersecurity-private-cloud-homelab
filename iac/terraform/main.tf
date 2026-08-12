terraform {
  required_version = ">= 1.5.0"
}

# Proxmox Provider & Network Segment Definitions
resource "null_resource" "vlan_10_trusted" {}
resource "null_resource" "vlan_20_servers" {}
resource "null_resource" "vlan_30_cyberlab" {}
resource "null_resource" "vlan_40_monitoring" {}
