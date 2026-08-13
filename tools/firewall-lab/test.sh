#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
evidence_dir="$repo_root/docs/evidence/executions/firewall"
summary="$evidence_dir/firewall-enforcement-summary.json"
results_file="$(mktemp)"
trap 'rm -f "$results_file"' EXIT
mkdir -p "$evidence_dir"
tool_version="$(docker exec hl-firewall nft --version | awk '{print $2}')"

counter() {
  local rule_id="$1"
  docker exec hl-firewall nft -j list chain inet homelab_filter forward |
    jq -r --arg rule_id "$rule_id" '[.nftables[].rule | select(.comment == $rule_id) | .expr[] | select(.counter) | .counter.packets][0]'
}

record_test() {
  local evidence_id="$1" scenario_id="$2" source_zone="$3" source_container="$4"
  local source_ip="$5" destination_ip="$6" port="$7" policy_rule="$8" expected="$9"
  local before after exit_code actual status command timestamp
  before="$(counter "$policy_rule")"
  command="nc -z -w 2 $destination_ip $port"
  set +e
  docker exec "$source_container" nc -z -w 2 "$destination_ip" "$port" >/dev/null 2>&1
  exit_code=$?
  set -e
  after="$(counter "$policy_rule")"
  timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  if [[ "$expected" == 'ALLOWED' ]]; then
    actual=$([[ $exit_code -eq 0 ]] && echo ALLOWED || echo DENIED)
    status=$([[ $exit_code -eq 0 && $after -gt $before ]] && echo PASS || echo FAIL)
  else
    actual=$([[ $exit_code -ne 0 ]] && echo "$expected" || echo UNEXPECTEDLY_ALLOWED)
    status=$([[ $exit_code -ne 0 && $after -gt $before ]] && echo PASS || echo FAIL)
  fi

  jq -n \
    --arg evidence_id "$evidence_id" --arg scenario_id "$scenario_id" \
    --arg source_zone "$source_zone" --arg source "$source_ip" \
    --arg destination "$destination_ip" --argjson port "$port" \
    --arg policy_rule "$policy_rule" --arg command "$command" \
    --arg timestamp "$timestamp" --arg expected "$expected" --arg actual "$actual" \
    --argjson exit_code "$exit_code" --argjson before "$before" --argjson after "$after" \
    --arg status "$status" \
    --arg tool_version "$tool_version" \
    '{evidence_id:$evidence_id,scenario_id:$scenario_id,classification:"EXECUTED_SYNTHETIC_TEST_EVIDENCE",implementation_class:"REFERENCE_POLICY_ENFORCEMENT",tool:"nftables",tool_version:$tool_version,source_zone:$source_zone,source:$source,destination:$destination,protocol:"TCP",port:$port,policy_rule:$policy_rule,command:$command,timestamp:$timestamp,expected_result:$expected,actual_result:$actual,connection_exit_code:$exit_code,counter_before:$before,counter_after:$after,verification_status:$status,limitations:"Isolated Docker nftables reference harness; does not prove pfSense, Proxmox, production deployment or operating effectiveness."}' >>"$results_file"

  [[ "$status" == 'PASS' ]]
}

docker exec hl-firewall nft -a list chain inet homelab_filter forward >"$evidence_dir/firewall-ruleset-before.txt"

record_test FW-EXEC-001 TRUSTED_TO_SERVER_SSH_ALLOW TRUSTED hl-trusted-host 10.10.10.10 10.10.20.15 22 FW-001 ALLOWED
record_test FW-EXEC-002 SERVER_TO_MONITORING_1514_ALLOW SERVERS hl-server-host 10.10.20.15 10.10.40.10 1514 FW-002 ALLOWED
record_test FW-EXEC-003 CYBERLAB_TO_SERVER_SSH_DENY CYBER_LAB hl-cyber-host 10.10.30.5 10.10.20.15 22 FW-004 DENIED_BY_FW_004
record_test FW-EXEC-004 CYBERLAB_TO_SERVER_443_DENY CYBER_LAB hl-cyber-host 10.10.30.5 10.10.20.15 443 FW-004 DENIED_BY_FW_004
record_test FW-EXEC-005 DEFAULT_DENY_TRUSTED_TO_MONITORING TRUSTED hl-trusted-host 10.10.10.10 10.10.40.10 9999 FW-005 DENIED_BY_FW_005
record_test FW-EXEC-006 DEFAULT_DENY_SERVERS_TO_TRUSTED SERVERS hl-server-host 10.10.20.15 10.10.10.10 9999 FW-005 DENIED_BY_FW_005
record_test FW-NEG-001 TRUSTED_TO_SERVER_PORT_23_DENY TRUSTED hl-trusted-host 10.10.10.10 10.10.20.15 23 FW-005 DENIED_BY_FW_005

docker exec hl-firewall nft -a list chain inet homelab_filter forward >"$evidence_dir/firewall-ruleset-after.txt"
jq -s --arg generated_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg tool_version "$tool_version" \
  '{schema_version:"1.0.0",generated_at:$generated_at,environment:"Docker Desktop isolated internal bridge networks",firewall_execution_path:"REFERENCE_NFTABLES",reference_base_image:"alpine@sha256:14358309a308569c32bdc37e2e0e9694be33a9d99e68afb0f5ff33cc1f695dce",reference_image:"homelab-firewall-reference:local",firewall_tool:"nftables",firewall_tool_version:$tool_version,network_segment_count:4,synthetic_host_count:4,privileged_container_used:false,firewall_logging_observed:false,firewall_counters_observed:true,pfsense_execution_proven:false,proxmox_deployment_proven:false,control_effectiveness_claimed:false,tests:.}' \
  "$results_file" >"$summary"

test "$(jq '[.tests[] | select(.verification_status != "PASS")] | length' "$summary")" -eq 0
echo 'REFERENCE_POLICY_ENFORCEMENT_VALIDATED=true'
