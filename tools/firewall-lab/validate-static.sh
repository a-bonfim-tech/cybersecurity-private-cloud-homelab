#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
expected_base='FROM alpine@sha256:14358309a308569c32bdc37e2e0e9694be33a9d99e68afb0f5ff33cc1f695dce'

grep -Fxq "$expected_base" "$script_dir/Dockerfile"
for file in Dockerfile README.md setup.sh test.sh cleanup.sh rules.nft validate-static.sh; do
  test -f "$script_dir/$file"
done
bash -n "$script_dir/setup.sh" "$script_dir/test.sh" "$script_dir/cleanup.sh" "$script_dir/validate-static.sh"
for rule_id in FW-001 FW-002 FW-004 FW-005; do
  grep -q "$rule_id" "$script_dir/rules.nft"
done
! grep -R --exclude=validate-static.sh --fixed-strings -- '--privileged' "$script_dir"
test "$(grep -c -- '--internal' "$script_dir/setup.sh")" -eq 4
for cidr in 10.10.10.0/24 10.10.20.0/24 10.10.30.0/24 10.10.40.0/24; do
  grep -q "$cidr" "$script_dir/setup.sh"
done

if [[ "${SKIP_NFT_IMAGE_PARSE:-0}" != '1' ]]; then
  docker build --tag homelab-firewall-reference:local "$script_dir" >/dev/null
  docker run --rm --cap-drop ALL --cap-add NET_ADMIN \
    --mount "type=bind,src=$script_dir/rules.nft,dst=/lab/rules.nft,readonly" \
    homelab-firewall-reference:local nft --check --file /lab/rules.nft
fi

echo 'FIREWALL_STATIC_VALIDATION=PASS'
