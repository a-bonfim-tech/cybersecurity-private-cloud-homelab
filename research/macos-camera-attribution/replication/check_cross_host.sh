#!/usr/bin/env bash
set -euo pipefail

REFERENCE_HOST_ID="${REFERENCE_HOST_ID:-d2c70c9a2614}"

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    exit 1
}

[[ "$(uname -s)" == "Darwin" ]] \
    || fail "cross-host camera replication requires macOS"

uuid="$(
    ioreg -rd1 -c IOPlatformExpertDevice \
    | awk -F'"' '/IOPlatformUUID/{print $4}'
)"

[[ -n "$uuid" ]] \
    || fail "unable to obtain platform identity input"

host_id="$(
    printf '%s\n' "$uuid" \
    | shasum -a 256 \
    | awk '{print substr($1,1,12)}'
)"

printf 'reference_host_id=%s\n' "$REFERENCE_HOST_ID"
printf 'candidate_host_id=%s\n' "$host_id"

if [[ "$host_id" == "$REFERENCE_HOST_ID" ]]; then
    fail "candidate is not an independent replication host"
fi

echo "INDEPENDENT_HOST_ID=PASS"
