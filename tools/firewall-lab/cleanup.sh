#!/usr/bin/env bash
set -euo pipefail

containers=(hl-firewall hl-trusted-host hl-server-host hl-cyber-host hl-monitor-host)
networks=(hl-trusted hl-servers hl-cyberlab hl-monitoring)

for container in "${containers[@]}"; do
  if docker container inspect "$container" >/dev/null 2>&1; then
    docker container rm --force "$container" >/dev/null
  fi
done

for network in "${networks[@]}"; do
  if docker network inspect "$network" >/dev/null 2>&1; then
    docker network rm "$network" >/dev/null
  fi
done

remaining_containers="$(docker container ls --all --filter 'name=^/hl-' --format '{{.Names}}')"
remaining_networks="$(docker network ls --filter 'name=^hl-' --format '{{.Name}}')"

test -z "$remaining_containers"
test -z "$remaining_networks"

echo 'REFERENCE_LAB_CLEANUP_VERIFIED=true'
