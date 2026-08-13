#!/usr/bin/env bash
set -euo pipefail

repository_root=$(cd "$(dirname "$0")/.." && pwd)
cd "$repository_root"

image=${WAZUH_IMAGE:-wazuh/wazuh-manager@sha256:c364ef100ba40d501537b1668a5a72bba4c4fbcf39bbef6a02123ff221fc40d0}
container="homelab-wazuh-logtest-$$"
evidence_dir="$repository_root/docs/evidence/executions/wazuh"

cleanup() {
  docker rm -f "$container" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker run -d --name "$container" \
  --network none \
  --pids-limit 512 \
  --memory 2g \
  --cpus 2 \
  --security-opt no-new-privileges \
  --mount "type=bind,src=$repository_root/detections/wazuh/local_rules.xml,dst=/var/ossec/etc/rules/local_rules.xml,readonly" \
  --mount "type=bind,src=$evidence_dir,dst=/evidence,readonly" \
  "$image" >/dev/null

ready=false
for _ in $(seq 1 24); do
  if docker exec "$container" /bin/bash -lc \
    '/var/ossec/bin/wazuh-control status | grep -q "wazuh-analysisd is running"'; then
    ready=true
    break
  fi
  sleep 5
done
test "$ready" = true

positive_output=$(docker exec "$container" /bin/bash -lc \
  'cat /evidence/suricata-exec-001-wazuh-input.jsonl | /var/ossec/bin/wazuh-logtest -U 100010:7:json 2>&1')
grep -q "Unit test OK" <<<"$positive_output"
grep -q "id: '100010'" <<<"$positive_output"
grep -Fq "mitre.id: '['T1046']'" <<<"$positive_output"

for input in WAZUH-NEG-001-input.jsonl WAZUH-NEG-002-input.jsonl; do
  output=$(docker exec "$container" /bin/bash -lc \
    "cat /evidence/$input | /var/ossec/bin/wazuh-logtest -v 2>&1")
  if grep -q "id: '100010'" <<<"$output"; then
    echo "unexpected rule 100010 match for $input" >&2
    exit 1
  fi
done

echo "Wazuh positive assertion and two bounded negative controls passed."
