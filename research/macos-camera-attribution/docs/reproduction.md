# Reproduction

Requirements:

- macOS
- `/usr/bin/log`
- `/usr/bin/sqlite3`
- `/usr/bin/shasum`
- `/usr/bin/codesign`
- Python 3

Run a bounded experiment:

    ./research/macos-camera-attribution/tools/collect_run.sh baseline 10

The second argument is collection duration in seconds.

For an interactive condition, prepare the desired application state before
starting the collector or use a sufficiently long bounded window and perform
the action during the interval.

After collection:

    python3 research/macos-camera-attribution/tools/normalize_timeline.py \
      research/macos-camera-attribution/evidence/runs/<RUN_ID>

    python3 research/macos-camera-attribution/tools/validate_module.py \
      research/macos-camera-attribution/evidence/runs/<RUN_ID>

Raw runs remain ignored by Git.
