#!/bin/bash
set -euo pipefail
umask 077

SCENARIO="${1:-}"
DURATION="${2:-10}"

if [[ -z "$SCENARIO" ]]; then
  echo "usage: $0 <scenario> [duration-seconds]" >&2
  exit 2
fi

if ! [[ "$DURATION" =~ ^[0-9]+$ ]] || (( DURATION < 1 || DURATION > 600 )); then
  echo "duration must be an integer between 1 and 600 seconds" >&2
  exit 2
fi

if [[ "$SCENARIO" == "control-a-no-chatgpt" ]]; then
  INITIAL_PIDS="$(pgrep -x "ChatGPT Classic" 2>/dev/null || true)"

  if [[ -n "$INITIAL_PIDS" ]]; then
    echo "PRECONDITION_FAIL: ChatGPT Classic is running" >&2
    printf '%s\n' "$INITIAL_PIDS" >&2
    exit 3
  fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

UTC="$(date -u '+%Y%m%dT%H%M%SZ')"
SAFE_SCENARIO="$(printf '%s' "$SCENARIO" | tr -cs 'A-Za-z0-9._-' '_')"
RUN_ID="${UTC}-${SAFE_SCENARIO}"
RUN_DIR="$MODULE_ROOT/evidence/runs/$RUN_ID"
RAW="$RUN_DIR/raw"

if ! mkdir "$RUN_DIR"; then
  echo "refusing existing or non-exclusive run directory: $RUN_DIR" >&2
  exit 5
fi
mkdir "$RAW"

START_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
START_LOCAL="$(date '+%Y-%m-%d %H:%M:%S')"
TZ_NAME="$(date '+%Z')"
UTC_OFFSET="$(date '+%z')"

{
  echo "run_id=$RUN_ID"
  echo "scenario=$SCENARIO"
  echo "duration_seconds=$DURATION"
  echo "start_utc=$START_UTC"
  echo "start_local=$START_LOCAL"
  echo "timezone=$TZ_NAME"
  echo "utc_offset=$UTC_OFFSET"
} > "$RAW/run-metadata.txt"

{
  sw_vers 2>&1 || true
  uname -a 2>&1 || true
  printf 'hardware_model='
  sysctl -n hw.model 2>/dev/null || true
  printf 'architecture='
  uname -m
} > "$RAW/system.txt"

APP="/Applications/ChatGPT Classic.app"

if [[ -d "$APP" ]]; then
  INFO="$APP/Contents/Info.plist"
  BIN="$APP/Contents/MacOS/ChatGPT Classic"

  {
    echo "application_path=$APP"

    if [[ -f "$INFO" ]]; then
      /usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$INFO" 2>/dev/null |
        sed 's/^/bundle_id=/' || true
      /usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$INFO" 2>/dev/null |
        sed 's/^/version=/' || true
    fi

    if [[ -f "$BIN" ]]; then
      codesign -dv "$BIN" 2>&1 || true
      shasum -a 256 "$BIN" 2>&1 || true
    fi
  } > "$RAW/application.txt"
else
  echo "application_not_present=$APP" > "$RAW/application.txt"
fi

ps -axo pid=,ppid=,uid=,user=,comm=,args= > "$RAW/processes-before.txt"

PIDS="$(pgrep -x 'ChatGPT Classic' 2>/dev/null || true)"

if [[ "$SCENARIO" == "control-a-no-chatgpt" && -n "$PIDS" ]]; then
  echo "PRECONDITION_RACE_FAIL: ChatGPT Classic appeared before collection" >&2
  printf '%s\n' "$PIDS" >&2
  exit 4
fi
if [[ -n "$PIDS" ]]; then
  printf '%s\n' "$PIDS" > "$RAW/target-pids-before.txt"
else
  : > "$RAW/target-pids-before.txt"
fi

if [[ -n "$PIDS" ]]; then
  : > "$RAW/network-before.txt"
  while IFS= read -r pid; do
    [[ -n "$pid" ]] || continue
    echo "===== PID $pid =====" >> "$RAW/network-before.txt"
    lsof -nP -a -p "$pid" -i >> "$RAW/network-before.txt" 2>&1 || true
  done <<< "$PIDS"
else
  echo "no_target_pid_observed" > "$RAW/network-before.txt"
fi

TCC_DB="$HOME/Library/Application Support/com.apple.TCC/TCC.db"

if [[ -r "$TCC_DB" ]]; then
  /usr/bin/sqlite3 -readonly "$TCC_DB" <<'SQL' > "$RAW/tcc-before.txt" 2>&1 || true
.headers on
.mode tabs
SELECT service,
       client,
       client_type,
       auth_value,
       auth_reason,
       last_modified
FROM access
WHERE lower(client) LIKE '%openai%'
   OR service IN (
      'kTCCServiceCamera',
      'kTCCServiceMicrophone',
      'kTCCServiceAudioCapture',
      'kTCCServiceScreenCapture',
      'kTCCServiceListenEvent'
   )
ORDER BY service, client;
SQL
else
  echo "TCC database not readable" > "$RAW/tcc-before.txt"
fi

sleep "$DURATION"

END_LOCAL="$(date '+%Y-%m-%d %H:%M:%S')"
END_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

{
  echo "end_utc=$END_UTC"
  echo "end_local=$END_LOCAL"
} >> "$RAW/run-metadata.txt"

/usr/bin/log show \
  --start "$START_LOCAL" \
  --end "$END_LOCAL" \
  --style syslog \
  --info \
  --debug \
  --predicate \
  'process == "ChatGPT Classic" OR
   process == "appleh13camerad" OR
   process == "cameracaptured" OR
   process == "tccd" OR
   process == "runningboardd" OR
   process == "ContinuityCaptureAgent" OR
   process == "ControlCenter"' \
  > "$RAW/unified.log" 2>&1 || true

ps -axo pid=,ppid=,uid=,user=,comm=,args= > "$RAW/processes-after.txt"

PIDS_AFTER="$(pgrep -x 'ChatGPT Classic' 2>/dev/null || true)"

CONTROL_VALID=""
CONTROL_INVALID_REASON=""

if [[ "$SCENARIO" == "control-a-no-chatgpt" ]]; then
  CONTROL_VALID="true"

  if [[ -n "$PIDS_AFTER" ]]; then
    CONTROL_VALID="false"
    CONTROL_INVALID_REASON="ChatGPT Classic appeared during control window"
  fi
fi
if [[ -n "$PIDS_AFTER" ]]; then
  printf '%s\n' "$PIDS_AFTER" > "$RAW/target-pids-after.txt"
else
  : > "$RAW/target-pids-after.txt"
fi

if [[ -n "$PIDS_AFTER" ]]; then
  : > "$RAW/network-after.txt"
  while IFS= read -r pid; do
    [[ -n "$pid" ]] || continue
    echo "===== PID $pid =====" >> "$RAW/network-after.txt"
    lsof -nP -a -p "$pid" -i >> "$RAW/network-after.txt" 2>&1 || true
  done <<< "$PIDS_AFTER"
else
  echo "no_target_pid_observed" > "$RAW/network-after.txt"
fi

if [[ -r "$TCC_DB" ]]; then
  /usr/bin/sqlite3 -readonly "$TCC_DB" <<'SQL' > "$RAW/tcc-after.txt" 2>&1 || true
.headers on
.mode tabs
SELECT service,
       client,
       client_type,
       auth_value,
       auth_reason,
       last_modified
FROM access
WHERE lower(client) LIKE '%openai%'
   OR service IN (
      'kTCCServiceCamera',
      'kTCCServiceMicrophone',
      'kTCCServiceAudioCapture',
      'kTCCServiceScreenCapture',
      'kTCCServiceListenEvent'
   )
ORDER BY service, client;
SQL
fi

{
  if [[ -n "$CONTROL_VALID" ]]; then
    echo "control_valid=$CONTROL_VALID"
  fi

  if [[ -n "$CONTROL_INVALID_REASON" ]]; then
    echo "control_invalid_reason=$CONTROL_INVALID_REASON"
  fi
} >> "$RAW/run-metadata.txt"

python3 "$SCRIPT_DIR/build_manifest.py" "$RUN_DIR"

echo
echo "RUN_ID=$RUN_ID"
echo "RUN_DIR=$RUN_DIR"
echo "Review raw evidence before any Git inclusion."
