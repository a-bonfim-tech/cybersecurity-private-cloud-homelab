#!/usr/bin/env bash
set -euo pipefail

MODULE="${MODULE:-research/macos-camera-attribution}"
ROOT="$MODULE/evidence/runs"
REPL="$MODULE/replication"

COLLECTOR="$MODULE/tools/collect_run.sh"
NORMALIZER="$MODULE/tools/normalize_timeline.py"
DERIVED_BUILDER="$MODULE/tools/build_derived_manifest.py"
MODULE_VALIDATOR="$MODULE/tools/validate_module.py"
COMPARATOR="$REPL/compare_runs.py"
REPLICATION_VALIDATOR="$REPL/validate_replication.py"

A1_SECONDS="${A1_SECONDS:-20}"
B_SECONDS="${B_SECONDS:-30}"
A2_SECONDS="${A2_SECONDS:-20}"

FORCE_FAIL_STAGE="${REPLICATION_FORCE_FAIL_STAGE:-}"

RUN_A1=""
RUN_B=""
RUN_A2=""
RESULT=""
HOST_FILE=""
HOST_ID=""

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    exit 1
}

forced_failure() {
    local stage="$1"

    if [[ "$FORCE_FAIL_STAGE" == "$stage" ]]; then
        fail "forced replication failure at stage=$stage"
    fi
}

require_command() {
    local command_name="$1"

    command -v "$command_name" >/dev/null 2>&1 \
        || fail "required command unavailable: $command_name"
}

require_file() {
    local path="$1"

    [[ -f "$path" ]] \
        || fail "required file missing: $path"
}

require_executable() {
    local path="$1"

    [[ -x "$path" ]] \
        || fail "required executable missing: $path"
}

cleanup() {
    osascript \
        -e 'tell application "QuickTime Player" to quit' \
        >/dev/null 2>&1 \
        || true
}

trap cleanup EXIT INT TERM

wait_for_quicktime_exit() {
    local i

    for i in {1..20}; do
        if ! pgrep -x "QuickTime Player" >/dev/null 2>&1; then
            return 0
        fi

        sleep 0.5
    done

    return 1
}

quit_quicktime() {
    osascript \
        -e 'tell application "QuickTime Player" to quit' \
        >/dev/null 2>&1 \
        || true

    wait_for_quicktime_exit \
        || fail "QuickTime Player failed to terminate"
}

open_clean_quicktime() {
    local docs
    local pid

    open -a "/System/Applications/QuickTime Player.app"
    sleep 4

    pid="$(
        pgrep -x "QuickTime Player" \
        | head -1 \
        || true
    )"

    [[ -n "$pid" ]] \
        || fail "QuickTime Player is not running"

    docs="$(
        osascript \
            -e 'tell application "QuickTime Player" to return count of documents'
    )"

    [[ "$docs" =~ ^[0-9]+$ ]] \
        || fail "invalid QuickTime document count: $docs"

    [[ "$docs" -eq 0 ]] \
        || fail "clean QuickTime state requires zero documents; observed=$docs"

    printf 'quicktime_pid=%s\n' "$pid"
    printf 'documents=%s\n' "$docs"
}

derive_host_id() {
    local uuid

    uuid="$(
        ioreg -rd1 -c IOPlatformExpertDevice \
        | awk -F'"' '/IOPlatformUUID/{print $4}'
    )"

    [[ -n "$uuid" ]] \
        || fail "unable to read platform identity input"

    # Preserve the original host-ID derivation semantics:
    # hash the UUID plus one LF. This keeps the pseudonym stable
    # with previously retained replication metadata.
    printf '%s\n' "$uuid" \
        | shasum -a 256 \
        | awk '{print substr($1,1,12)}'
}

capture_host_metadata() {
    local host_file="$1"
    local host_id="$2"
    local captured_at
    local baseline_commit

    captured_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    baseline_commit="$(
        git rev-parse --short HEAD 2>/dev/null \
        || printf 'unknown'
    )"

    python3 - \
        "$host_file" \
        "$host_id" \
        "$captured_at" \
        "$baseline_commit" <<'PY'
from pathlib import Path
import json
import platform
import subprocess
import sys

out = Path(sys.argv[1])
host_id = sys.argv[2]
captured_at = sys.argv[3]
baseline_commit = sys.argv[4]

def cmd(*args: str) -> str:
    try:
        return subprocess.check_output(
            args,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"

def sysctl(name: str) -> str:
    return cmd("sysctl", "-n", name)

data = {
    "schema_version": 1,
    "host_id": host_id,
    "captured_at_utc": captured_at,
    "baseline_commit": baseline_commit,
    "platform": "macOS",
    "product_name": cmd("sw_vers", "-productName"),
    "product_version": cmd("sw_vers", "-productVersion"),
    "build_version": cmd("sw_vers", "-buildVersion"),
    "architecture": platform.machine(),
    "hardware_model": sysctl("hw.model"),
    "cpu_brand": sysctl("machdep.cpu.brand_string"),
    "physical_cpu_count": sysctl("hw.physicalcpu"),
    "logical_cpu_count": sysctl("hw.logicalcpu"),
    "memory_bytes": sysctl("hw.memsize"),
    "sip_status": cmd("csrutil", "status"),
    "filevault_status": cmd("fdesetup", "status"),
    "notes": (
        "Sanitized replication host metadata. "
        "Direct host, account, device, and network identifiers are excluded."
    ),
}

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(
    json.dumps(data, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
}

resolve_run() {
    local scenario="$1"
    local run

    run="$(
        find "$ROOT" \
            -mindepth 1 \
            -maxdepth 1 \
            -type d \
            -name "*-${scenario}" \
            | sort \
            | tail -1
    )"

    [[ -n "$run" ]] \
        || fail "unable to resolve collected run for scenario=$scenario"

    printf '%s\n' "$run"
}

process_run() {
    local run="$1"
    local label="$2"

    python3 "$NORMALIZER" "$run"
    python3 "$DERIVED_BUILDER" "$run"
    python3 "$MODULE_VALIDATOR" "$run"

    printf '%s_VALIDATION=PASS\n' "$label"
}

collect_scenario() {
    local scenario="$1"
    local seconds="$2"
    local label="$3"
    local run

    # Command substitution captures stdout. All operational logging
    # therefore goes to stderr so stdout contains only the resolved
    # run directory returned at the end of this function.
    "$COLLECTOR" "$scenario" "$seconds" >&2

    run="$(resolve_run "$scenario")"

    process_run "$run" "$label" >&2

    printf '%s\n' "$run"
}

assert_preview_established() {
    local docs
    local matching

    osascript <<'APPLESCRIPT'
tell application "QuickTime Player"
    activate
    new movie recording
end tell
APPLESCRIPT

    sleep 5

    docs="$(
        osascript \
            -e 'tell application "QuickTime Player" to return count of documents'
    )"

    [[ "$docs" =~ ^[0-9]+$ ]] \
        || fail "invalid QuickTime preview document count: $docs"

    [[ "$docs" -ge 1 ]] \
        || fail "QuickTime movie preview was not established"

    matching="$(
        /usr/bin/log show \
            --last 8s \
            --style compact \
            --predicate 'process == "appleh13camerad"' \
        | grep -Eic 'CMIOExtensionStream' \
        || true
    )"

    printf 'documents=%s\n' "$docs"
    printf 'preview_precheck_cmio_activity=%s\n' "$matching"

    [[ "$matching" -gt 0 ]] \
        || fail \
            "preview exists but primary observable was not seen during precheck"
}

assert_idle_precheck() {
    local matching

    matching="$(
        /usr/bin/log show \
            --last 5s \
            --style compact \
            --predicate 'process == "appleh13camerad"' \
        | grep -Eic 'CMIOExtensionStream' \
        || true
    )"

    printf 'idle_precheck_cmio_activity=%s\n' "$matching"

    [[ "$matching" -eq 0 ]] \
        || fail \
            "idle precheck contains CMIOExtensionStream activity"
}

printf '===== REPLICATION PREFLIGHT =====\n'

[[ "$(uname -s)" == "Darwin" ]] \
    || fail "this replication protocol requires macOS"

for command_name in \
    python3 \
    osascript \
    open \
    pgrep \
    ioreg \
    shasum \
    git
do
    require_command "$command_name"
done

require_executable "$COLLECTOR"

for required_file in \
    "$NORMALIZER" \
    "$DERIVED_BUILDER" \
    "$MODULE_VALIDATOR" \
    "$COMPARATOR" \
    "$REPLICATION_VALIDATOR"
do
    require_file "$required_file"
done

mkdir -p \
    "$ROOT" \
    "$REPL/hosts" \
    "$REPL/results"

forced_failure "preflight"

HOST_ID="$(derive_host_id)"
HOST_FILE="$REPL/hosts/${HOST_ID}.json"

EXECUTION_ID="$(
    date -u '+%Y%m%dT%H%M%SZ'
)"

RESULT_DIR="$REPL/results/$HOST_ID"
mkdir -p "$RESULT_DIR"

RESULT="$RESULT_DIR/${EXECUTION_ID}.json"

printf 'host_id=%s\n' "$HOST_ID"
printf 'execution_id=%s\n' "$EXECUTION_ID"

if [[ -f "$HOST_FILE" ]]; then
    printf 'host_metadata=existing\n'
else
    capture_host_metadata "$HOST_FILE" "$HOST_ID"
    printf 'host_metadata=created\n'
fi

printf '\n===== A1: IDLE CONTROL =====\n'

quit_quicktime
open_clean_quicktime

forced_failure "a1-condition"

printf 'A1_CONDITION=PASS\n'

SCENARIO_A1="replication-${HOST_ID}-a1-idle"
RUN_A1="$(
    collect_scenario \
        "$SCENARIO_A1" \
        "$A1_SECONDS" \
        "A1"
)"

forced_failure "a1-validation"

printf '\n===== B: PREVIEW ACTIVE =====\n'

assert_preview_established

forced_failure "b-condition"

printf 'B_CONDITION=PASS\n'

SCENARIO_B="replication-${HOST_ID}-b-preview"
RUN_B="$(
    collect_scenario \
        "$SCENARIO_B" \
        "$B_SECONDS" \
        "B"
)"

forced_failure "b-validation"

printf '\n===== A2: POST-PREVIEW IDLE CONTROL =====\n'

quit_quicktime
sleep 2
open_clean_quicktime
assert_idle_precheck

forced_failure "a2-condition"

printf 'A2_CONDITION=PASS\n'

SCENARIO_A2="replication-${HOST_ID}-a2-idle"
RUN_A2="$(
    collect_scenario \
        "$SCENARIO_A2" \
        "$A2_SECONDS" \
        "A2"
)"

forced_failure "a2-validation"

[[ "$RUN_A1" != "$RUN_B" ]] \
    || fail "A1 and B resolved to the same run"

[[ "$RUN_A1" != "$RUN_A2" ]] \
    || fail "A1 and A2 resolved to the same run"

[[ "$RUN_B" != "$RUN_A2" ]] \
    || fail "B and A2 resolved to the same run"

printf '\n===== COMPARISON =====\n'

python3 "$COMPARATOR" \
    --host-id "$HOST_ID" \
    --execution-id "$EXECUTION_ID" \
    --a1 "$RUN_A1" \
    --b "$RUN_B" \
    --a2 "$RUN_A2" \
    --output "$RESULT"

forced_failure "comparison"

printf '\n===== FINAL REPLICATION VALIDATION =====\n'

python3 "$REPLICATION_VALIDATOR" \
    --host-id "$HOST_ID" \
    --execution-id "$EXECUTION_ID" \
    --a1 "$RUN_A1" \
    --b "$RUN_B" \
    --a2 "$RUN_A2" \
    --host "$HOST_FILE" \
    --result "$RESULT"

forced_failure "final-validation"

printf '\n===== REPLICATION ARTIFACTS =====\n'
printf 'HOST_ID=%s\n' "$HOST_ID"
printf 'EXECUTION_ID=%s\n' "$EXECUTION_ID"
printf 'HOST_FILE=%s\n' "$HOST_FILE"
printf 'RUN_A1=%s\n' "$RUN_A1"
printf 'RUN_B=%s\n' "$RUN_B"
printf 'RUN_A2=%s\n' "$RUN_A2"
printf 'RESULT=%s\n' "$RESULT"

printf '\nRUN_REPLICATION=PASS\n'
