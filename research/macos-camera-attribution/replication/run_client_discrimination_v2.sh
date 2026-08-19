#!/usr/bin/env bash
set -euo pipefail

EXPERIMENT_TAG="macos-camera-client-discrimination-experiment-v2"
EXPERIMENT_COMMIT="784b29e68527011972899ef45975d0788e0cae8b"

MODULE="research/macos-camera-attribution"
ROOT="$MODULE/replication/client-discrimination-v2/results"

PHOTO_BOOTH_BUNDLE="com.apple.PhotoBooth"
QUICKTIME_BUNDLE="com.apple.QuickTimePlayerX"

EXECUTION_ID="$(date -u '+%Y%m%dT%H%M%SZ')"
OUTDIR="$ROOT/$EXECUTION_ID"
RESULT="$OUTDIR/result.json"

mkdir -p "$OUTDIR"

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

cmio_count() {
    local window="$1"

    /usr/bin/log show \
        --last "$window" \
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

quicktime_document_count() {
    /usr/bin/osascript <<'APPLESCRIPT'
tell application "QuickTime Player"
    return count of documents
end tell
APPLESCRIPT
}

photo_booth_bundle() {
    /usr/bin/osascript <<'APPLESCRIPT'
tell application "System Events"
    set matches to every application process whose bundle identifier is "com.apple.PhotoBooth"

    if (count of matches) is 0 then
        return ""
    end if

    return bundle identifier of item 1 of matches
end tell
APPLESCRIPT
}

write_abort() {
    local condition="$1"
    local reason="$2"

    python3 - "$RESULT" "$EXECUTION_ID" "$condition" "$reason" <<'PY'
import json
import sys
from pathlib import Path

result_path = Path(sys.argv[1])
execution_id = sys.argv[2]
condition = sys.argv[3]
reason = sys.argv[4]

doc = {
    "schema_version": 2,
    "execution_id": execution_id,
    "experiment": "quicktime-vs-photo-booth-v2",
    "outcome": "ABORTED_CONDITION_INVALID",
    "failed_condition": condition,
    "reason": reason,
    "usable_for_client_discrimination_claim": False,
    "claim_boundary": (
        "Provider stream-related activity only; "
        "not direct frame-delivery evidence."
    ),
}

result_path.write_text(
    json.dumps(doc, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

    python3 -m json.tool "$RESULT"
    exit 2
}

echo "===== CLIENT DISCRIMINATION V2 PREFLIGHT ====="
printf 'experiment_tag=%s\n' "$EXPERIMENT_TAG"
printf 'experiment_commit=%s\n' "$EXPERIMENT_COMMIT"
printf 'execution_id=%s\n' "$EXECUTION_ID"

[[ "$(git rev-parse "$EXPERIMENT_TAG^{commit}")" == "$EXPERIMENT_COMMIT" ]] \
    || fail "experiment tag mismatch"

echo
echo "===== A: IDLE ====="

QT_DOCS_A="$(quicktime_document_count 2>/dev/null || echo 0)"
A_CMIO="$(cmio_count 5s)"

printf 'quicktime_documents=%s\n' "$QT_DOCS_A"
printf 'A_CMIO=%s\n' "$A_CMIO"

[[ "$QT_DOCS_A" -eq 0 ]] \
    || write_abort "A" "QuickTime movie-recording document exists"

[[ "$A_CMIO" -eq 0 ]] \
    || write_abort "A" "CMIOExtensionStream activity present in idle control"

echo
echo "A_CONDITION=PASS"

echo
echo "Prepare condition B."
echo "QuickTime Player must have a New Movie Recording preview active."
echo "Press Enter only after the preview is visibly active."
read -r

echo
echo "===== B: QUICKTIME ====="

B_QT="$(quicktime_pid)"
QT_DOCS_B="$(quicktime_document_count 2>/dev/null || echo 0)"
B_CMIO="$(cmio_count 10s)"

printf 'quicktime_pid=%s\n' "${B_QT:-none}"
printf 'quicktime_documents=%s\n' "$QT_DOCS_B"
printf 'B_CMIO=%s\n' "$B_CMIO"

[[ -n "$B_QT" ]] \
    || write_abort "B" "QuickTime process not observed"

[[ "$QT_DOCS_B" -gt 0 ]] \
    || write_abort "B" "QuickTime movie-recording document not observed"

[[ "$B_CMIO" -gt 0 ]] \
    || write_abort "B" "QuickTime condition lacks CMIOExtensionStream activity"

echo
echo "B_CONDITION=PASS"

echo
echo "Close every QuickTime movie-recording document."
echo "Then press Enter."
read -r

QT_DOCS_AFTER_B="$(quicktime_document_count 2>/dev/null || echo 0)"

printf 'quicktime_documents_after_b=%s\n' "$QT_DOCS_AFTER_B"

[[ "$QT_DOCS_AFTER_B" -eq 0 ]] \
    || write_abort "B_TO_C" "QuickTime movie-recording document still open"

sleep 6

TRANSITION_CMIO="$(cmio_count 5s)"

printf 'transition_cmio=%s\n' "$TRANSITION_CMIO"

[[ "$TRANSITION_CMIO" -eq 0 ]] \
    || write_abort "B_TO_C" "provider activity did not return to idle"

echo
echo "Open Photo Booth and leave camera preview active."
echo "Then press Enter."
read -r

echo
echo "===== C: PHOTO BOOTH ====="

C_PB="$(photo_booth_pid)"
C_BUNDLE="$(photo_booth_bundle)"
QT_DOCS_C="$(quicktime_document_count 2>/dev/null || echo 0)"
C_CMIO="$(cmio_count 10s)"

printf 'photo_booth_pid=%s\n' "${C_PB:-none}"
printf 'photo_booth_bundle=%s\n' "${C_BUNDLE:-none}"
printf 'quicktime_documents=%s\n' "$QT_DOCS_C"
printf 'C_CMIO=%s\n' "$C_CMIO"

[[ -n "$C_PB" ]] \
    || write_abort "C" "Photo Booth process not observed"

[[ "$C_BUNDLE" == "$PHOTO_BOOTH_BUNDLE" ]] \
    || write_abort "C" "Photo Booth bundle identity not observed"

[[ "$QT_DOCS_C" -eq 0 ]] \
    || write_abort "C" "QuickTime movie-recording document present"

[[ "$C_CMIO" -gt 0 ]] \
    || write_abort "C" "Photo Booth condition lacks CMIOExtensionStream activity"

echo
echo "C_CONDITION=PASS"

python3 - \
    "$RESULT" \
    "$EXECUTION_ID" \
    "$A_CMIO" \
    "$B_CMIO" \
    "$C_CMIO" \
    "$B_QT" \
    "$C_PB" <<'PY'
import json
import sys
from pathlib import Path

(
    result_path,
    execution_id,
    a_cmio,
    b_cmio,
    c_cmio,
    b_qt,
    c_pb,
) = sys.argv[1:]

doc = {
    "schema_version": 2,
    "execution_id": execution_id,
    "experiment": "quicktime-vs-photo-booth-v2",
    "conditions": {
        "A": {
            "cmio_count": int(a_cmio),
            "gate": "PASS",
        },
        "B": {
            "client": "QuickTime Player",
            "quicktime_pid": b_qt,
            "cmio_count": int(b_cmio),
            "gate": "PASS",
        },
        "C": {
            "client": "Photo Booth",
            "bundle_id": "com.apple.PhotoBooth",
            "photo_booth_pid": c_pb,
            "cmio_count": int(c_cmio),
            "gate": "PASS",
        },
    },
    "valid_condition_contrast": True,
    "client_discriminator": None,
    "outcome": "PROVIDER_ONLY",
    "usable_for_client_discrimination_claim": False,
    "claim_boundary": (
        "Provider stream-related activity only; "
        "not direct frame-delivery evidence."
    ),
    "interpretation": (
        "A valid idle/QuickTime/Photo Booth provider contrast was observed. "
        "No directly observed client/provider discriminator was established."
    ),
}

Path(result_path).write_text(
    json.dumps(doc, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

echo
echo "===== RESULT ====="
python3 -m json.tool "$RESULT"

echo
echo "CLIENT_DISCRIMINATION_V2_RUN=PASS"
printf 'RESULT=%s\n' "$RESULT"
