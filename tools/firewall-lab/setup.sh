#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
image="homelab-firewall-reference:local"

"$script_dir/cleanup.sh"
docker build --tag "$image" "$script_dir"

docker network create --internal --subnet 10.10.10.0/24 hl-trusted >/dev/null
docker network create --internal --subnet 10.10.20.0/24 hl-servers >/dev/null
docker network create --internal --subnet 10.10.30.0/24 hl-cyberlab >/dev/null
docker network create --internal --subnet 10.10.40.0/24 hl-monitoring >/dev/null

docker run --detach --name hl-firewall \
  --cap-drop ALL --cap-add NET_ADMIN --cap-add NET_RAW \
  --sysctl net.ipv4.ip_forward=1 \
  --network hl-trusted --ip 10.10.10.254 \
  --mount "type=bind,src=$script_dir/rules.nft,dst=/lab/rules.nft,readonly" \
  "$image" >/dev/null
docker network connect --ip 10.10.20.254 hl-servers hl-firewall
docker network connect --ip 10.10.30.254 hl-cyberlab hl-firewall
docker network connect --ip 10.10.40.254 hl-monitoring hl-firewall

docker run --detach --name hl-trusted-host --cap-drop ALL --cap-add NET_ADMIN \
  --network hl-trusted --ip 10.10.10.10 "$image" >/dev/null
docker run --detach --name hl-server-host --cap-drop ALL --cap-add NET_ADMIN \
  --network hl-servers --ip 10.10.20.15 "$image" >/dev/null
docker run --detach --name hl-cyber-host --cap-drop ALL --cap-add NET_ADMIN \
  --network hl-cyberlab --ip 10.10.30.5 "$image" >/dev/null
docker run --detach --name hl-monitor-host --cap-drop ALL --cap-add NET_ADMIN \
  --network hl-monitoring --ip 10.10.40.10 "$image" >/dev/null

# Docker Desktop isolates distinct bridge networks before a router container can
# receive ordinary cross-subnet frames. Bounded IP-in-IP links carry only the
# synthetic zone packets to the firewall namespace; nftables still evaluates
# and forwards the original 10.10.x source and destination addresses.
for endpoint in \
  'hl-trusted-host eth0 10.10.10.9/24 10.10.10.9 10.10.10.253' \
  'hl-server-host eth0 10.10.20.14/24 10.10.20.14 10.10.20.253' \
  'hl-cyber-host eth0 10.10.30.4/24 10.10.30.4 10.10.30.253' \
  'hl-monitor-host eth0 10.10.40.9/24 10.10.40.9 10.10.40.253'; do
  read -r container interface alias_cidr local_outer remote_outer <<<"$endpoint"
  docker exec "$container" ip addr add "$alias_cidr" dev "$interface"
  docker exec "$container" ip tunnel add hl-zone mode ipip local "$local_outer" remote "$remote_outer"
  docker exec "$container" ip link set hl-zone up
done

docker exec hl-firewall ip addr add 10.10.10.253/24 dev eth0
docker exec hl-firewall ip addr add 10.10.20.253/24 dev eth1
docker exec hl-firewall ip addr add 10.10.30.253/24 dev eth2
docker exec hl-firewall ip addr add 10.10.40.253/24 dev eth3

for tunnel in \
  'hl-trusted-tun 10.10.10.253 10.10.10.9' \
  'hl-server-tun 10.10.20.253 10.10.20.14' \
  'hl-cyber-tun 10.10.30.253 10.10.30.4' \
  'hl-monitor-tun 10.10.40.253 10.10.40.9'; do
  read -r name local_outer remote_outer <<<"$tunnel"
  docker exec hl-firewall ip tunnel add "$name" mode ipip local "$local_outer" remote "$remote_outer"
  docker exec hl-firewall ip link set "$name" up
done

for route in \
  'hl-trusted-host 10.10.20.0/24 10.10.10.10' \
  'hl-trusted-host 10.10.30.0/24 10.10.10.10' \
  'hl-trusted-host 10.10.40.0/24 10.10.10.10' \
  'hl-server-host 10.10.10.0/24 10.10.20.15' \
  'hl-server-host 10.10.30.0/24 10.10.20.15' \
  'hl-server-host 10.10.40.0/24 10.10.20.15' \
  'hl-cyber-host 10.10.10.0/24 10.10.30.5' \
  'hl-cyber-host 10.10.20.0/24 10.10.30.5' \
  'hl-cyber-host 10.10.40.0/24 10.10.30.5' \
  'hl-monitor-host 10.10.10.0/24 10.10.40.10' \
  'hl-monitor-host 10.10.20.0/24 10.10.40.10' \
  'hl-monitor-host 10.10.30.0/24 10.10.40.10'; do
  read -r container subnet source_ip <<<"$route"
  docker exec "$container" ip route replace "$subnet" dev hl-zone src "$source_ip"
done

docker exec hl-firewall ip route replace 10.10.10.10/32 dev hl-trusted-tun
docker exec hl-firewall ip route replace 10.10.20.15/32 dev hl-server-tun
docker exec hl-firewall ip route replace 10.10.30.5/32 dev hl-cyber-tun
docker exec hl-firewall ip route replace 10.10.40.10/32 dev hl-monitor-tun

docker exec hl-firewall nft -f /lab/rules.nft
docker exec --detach hl-server-host sh -c 'while true; do nc -l -p 22 >/dev/null 2>&1; done'
docker exec --detach hl-monitor-host sh -c 'while true; do nc -l -p 1514 >/dev/null 2>&1; done'

test "$(docker exec hl-firewall cat /proc/sys/net/ipv4/ip_forward)" = '1'
echo 'REFERENCE_HARNESS_READY=true'
