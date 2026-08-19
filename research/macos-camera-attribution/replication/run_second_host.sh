#!/usr/bin/env bash
set -euo pipefail

REFERENCE_HOST_ID="${REFERENCE_HOST_ID:-d2c70c9a2614}"

PROTOCOL_TAG="macos-camera-attribution-cross-host-protocol-v1"
BASELINE_TAG="macos-camera-attribution-replication-v2"
BASELINE_COMMIT="a0f1ff4264879fe630da047d0ec45762f0fd2dd0"

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    exit 1
}

[[ "$(uname -s)" == "Darwin" ]] \
    || fail "second-host replication requires macOS"

command -v git >/dev/null 2>&1 \
    || fail "git is required"

command -v python3 >/dev/null 2>&1 \
    || fail "python3 is required"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" \
    || fail "run inside a repository clone"

cd "$ROOT"

printf '===== SECOND-HOST REPLICATION GATE =====\n'
printf 'repo=%s\n' "$ROOT"
printf 'reference_host_id=%s\n' "$REFERENCE_HOST_ID"

git fetch --tags origin

git rev-parse "$PROTOCOL_TAG^{commit}" >/dev/null
git rev-parse "$BASELINE_TAG^{commit}" >/dev/null

observed_baseline="$(
    git rev-parse "$BASELINE_TAG^{commit}"
)"

printf 'baseline_tag=%s\n' "$BASELINE_TAG"
printf 'baseline_commit=%s\n' "$observed_baseline"

[[ "$observed_baseline" == "$BASELINE_COMMIT" ]] \
    || fail "frozen baseline tag does not resolve to expected commit"

printf '\n===== INDEPENDENT HOST CHECK =====\n'

git checkout --detach "$PROTOCOL_TAG"

REFERENCE_HOST_ID="$REFERENCE_HOST_ID" \
    research/macos-camera-attribution/replication/check_cross_host.sh

printf '\n===== FROZEN BASELINE CHECKOUT =====\n'

git checkout --detach "$BASELINE_TAG"

[[ "$(git rev-parse HEAD)" == "$BASELINE_COMMIT" ]] \
    || fail "unexpected frozen baseline checkout"

MODULE="research/macos-camera-attribution"
REPL="$MODULE/replication"

printf 'head=%s\n' "$(git rev-parse HEAD)"

printf '\n===== STATIC PREFLIGHT =====\n'

python3 -m unittest discover \
    -s "$MODULE/tests" \
    -p 'test_*.py' \
    -v

bash -n "$REPL/run_replication.sh"

python3 -m py_compile \
    "$REPL/compare_runs.py" \
    "$REPL/validate_replication.py"

printf '\nSECOND_HOST_STATIC_GATE=PASS\n'

printf '\n===== EXPERIMENT =====\n'

"$REPL/run_replication.sh"

printf '\nSECOND_HOST_REPLICATION_EXECUTION=COMPLETE\n'
printf 'Review generated raw evidence locally before any Git inclusion.\n'
printf 'Retain the result regardless of outcome.\n'
