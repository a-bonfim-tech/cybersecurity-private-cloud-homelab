#!/usr/bin/env bash
set -euo pipefail

repository_root=$(cd "$(dirname "$0")/.." && pwd)
cd "$repository_root"

test_root=$(mktemp -d "${TMPDIR:-/tmp}/homelab-suricata.XXXXXX")
trap 'rm -rf "$test_root"' EXIT
mkdir -p "$test_root/config"

suricata -T -l "$test_root/config" \
  -c tests/suricata/suricata.yaml \
  -S detections/suricata/local.rules

run_case() {
  case_name=$1
  pcap=$2
  expected_alerts=$3
  output="$test_root/$case_name"
  mkdir -p "$output"
  suricata -r "$pcap" -l "$output" \
    -c tests/suricata/suricata.yaml \
    -S detections/suricata/local.rules
  actual_alerts=$(jq -s '[.[] | select(.event_type == "alert" and .alert.signature_id == 1000001)] | length' "$output/eve.json")
  test "$actual_alerts" -eq "$expected_alerts"
  printf '%s alerts=%s expected=%s\n' "$case_name" "$actual_alerts" "$expected_alerts"
}

run_case positive docs/evidence/pcaps/recon_vlan30_to_vlan20_positive_scan.pcap 1
run_case negative_below_threshold docs/evidence/pcaps/recon_vlan30_to_vlan20_negative_below_threshold.pcap 0
run_case negative_ack docs/evidence/pcaps/recon_vlan30_to_vlan20_negative_ack.pcap 0
