#!/usr/bin/env bash
set -euo pipefail

EXPERIMENT_TAG="macos-camera-client-discrimination-experiment-v1"
EXPERIMENT_COMMIT="cb0ffbfb6ce6996700855fd962745beff5136648"

PHOTO_BOOTH="/System/Applications/Photo Booth.app"
PHOTO_BOOTH_BUNDLE="com.apple.PhotoBooth"

CLAIM_BOUNDARY="Provider stream-related activity only; not direct frame-delivery evidence."

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    exit 1
}

[[ "$(uname -s)" == "Darwin" ]] \
    || fail "client discrimination requires macOS"

git cat-file -e "${EXPERIMENT_TAG}^{commit}" 2>/dev/null \
    || fail "experiment tag unavailable"

observed="$(
    git rev-list -n 1 "$EXPERIMENT_TAG"
)"

[[ "$observed" == "$EXPERIMENT_COMMIT" ]] \
    || fail "experiment tag does not resolve to frozen commit"

[[ -d "$PHOTO_BOOTH" ]] \
    || fail "Photo Booth unavailable"

bundle="$(
    /usr/libexec/PlistBuddy \
        -c 'Print :CFBundleIdentifier' \
        "$PHOTO_BOOTH/Contents/Info.plist"
)"

[[ "$bundle" == "$PHOTO_BOOTH_BUNDLE" ]] \
    || fail "unexpected Photo Booth bundle identifier"

MODULE="research/macos-camera-attribution"
OUTROOT="$MODULE/replication/client-discrimination/results"

EXECUTION_ID="$(
    date -u '+%Y%m%dT%H%M%SZ'
)"

OUTDIR="$OUTROOT/$EXECUTION_ID"
mkdir -p "$OUTDIR"

process_snapshot() {
    local label="$1"

    /bin/ps \
        -axo pid=,ppid=,uid=,comm=,args= \
        > "$OUTDIR/${label}-processes.txt"
}

cmio_count() {
    /usr/bin/log show \
        --last 15s \
        --style compact \
        --predicate 'process == "appleh13camerad"' \
        2>/dev/null \
    | grep -Eic 'CMIOExtensionStream' \
    || true
}

quicktime_pid() {
    pgrep -x "QuickTime Player" \
    | head -1 \
    || true
}

photo_booth_pid() {
    pgrep -x "Photo Booth" \
    | head -1 \
    || true
}

printf '===== CLIENT DISCRIMINATION PREFLIGHT =====\n'
printf 'experiment_tag=%s\n' "$EXPERIMENT_TAG"
printf 'experiment_commit=%s\n' "$EXPERIMENT_COMMIT"
printf 'execution_id=%s\n' "$EXECUTION_ID"

printf '\n===== A: IDLE =====\n'

A_QT="$(quicktime_pid)"
A_PB="$(photo_booth_pid)"

process_snapshot "a-idle"

A_COUNT="$(cmio_count)"

printf 'quicktime_pid=%s\n' "${A_QT:-none}"
printf 'photo_booth_pid=%s\n' "${A_PB:-none}"
printf 'cmio_count=%s\n' "$A_COUNT"

printf '\nPrepare condition B manually:\n'
printf 'Open QuickTime Player -> File -> New Movie Recording.\n'
printf 'Leave preview active, then press Enter.\n'
read -r

printf '\n===== B: QUICKTIME =====\n'

B_QT="$(quicktime_pid)"
[[ -n "$B_QT" ]] \
    || fail "QuickTime Player PID not observed"

B_PB="$(photo_booth_pid)"

process_snapshot "b-quicktime"

B_COUNT="$(cmio_count)"

printf 'quicktime_pid=%s\n' "$B_QT"
printf 'photo_booth_pid=%s\n' "${B_PB:-none}"
printf 'cmio_count=%s\n' "$B_COUNT"

printf '\nClose QuickTime movie preview completely.\n'
printf 'Open Photo Booth and leave camera preview active.\n'
printf 'Then press Enter.\n'
read -r

printf '\n===== C: PHOTO BOOTH =====\n'

C_PB="$(photo_booth_pid)"
[[ -n "$C_PB" ]] \
    || fail "Photo Booth PID not observed"

C_QT="$(quicktime_pid)"

process_snapshot "c-photo-booth"

C_COUNT="$(cmio_count)"

printf 'quicktime_pid=%s\n' "${C_QT:-none}"
printf 'photo_booth_pid=%s\n' "$C_PB"
printf 'cmio_count=%s\n' "$C_COUNT"

RESULT="$OUTDIR/result.json"

python3 - \
    "$RESULT" \
    "$EXECUTION_ID" \
    "$A_COUNT" \
    "$B_COUNT" \
    "$C_COUNT" \
    "${A_QT:-}" \
    "${A_PB:-}" \
    "${B_QT:-}" \
    "${B_PB:-}" \
    "${C_QT:-}" \
    "${C_PB:-}" \
    "$CLAIM_BOUNDARY" <<'PY'
from pathlib import Path
import json
import sys

(
    result_path,
    execution_id,
    a_count,
    b_count,
    c_count,
    a_qt,
    a_pb,
    b_qt,
    b_pb,
    c_qt,
    c_pb,
    claim_boundary,
) = sys.argv[1:]

a_count = int(a_count)
b_count = int(b_count)
c_count = int(c_count)

# Classification is deliberately conservative.
#
# Provider activity alone cannot support client discrimination.
# PID presence in process snapshots also does not establish causal linkage
# between client and provider events.
#
# Until a directly observed client/provider linkage is retained,
# the maximum positive classification is PROVIDER_ONLY.

if a_count == 0 and b_count > 0 and c_count > 0:
    outcome = "PROVIDER_ONLY"
else:
    outcome = "INCONCLUSIVE"

doc = {
    "schema_version": 1,
    "execution_id": execution_id,
    "experiment": "quicktime-vs-photo-booth",
    "conditions": {
        "A": {
            "client": "idle",
            "cmio_count": a_count,
            "quicktime_pid": a_qt or None,
            "photo_booth_pid": a_pb or None,
        },
        "B": {
            "client": "QuickTime Player",
            "cmio_count": b_count,
            "quicktime_pid": b_qt or None,
            "photo_booth_pid": b_pb or None,
        },
        "C": {
            "client": "Photo Booth",
            "bundle_id": "com.apple.PhotoBooth",
            "cmio_count": c_count,
            "quicktime_pid": c_qt or None,
            "photo_booth_pid": c_pb or None,
        },
    },
    "outcome": outcome,
    "client_discriminator": None,
    "claim_boundary": claim_boundary,
    "interpretation": (
        "Provider activity may distinguish camera-active conditions "
        "from idle. Client discrimination is not established without "
        "a directly observed client/provider linkage."
    ),
}

Path(result_path).write_text(
    json.dumps(doc, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

printf '\n===== RESULT =====\n'
python3 -m json.tool "$RESULT"

printf '\nCLIENT_DISCRIMINATION_RUN=PASS\n'
printf 'RESULT=%s\n' "$RESULT"
printf 'Review all local evidence before any Git inclusion.\n'
