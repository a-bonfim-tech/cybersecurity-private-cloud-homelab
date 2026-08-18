# Experiment Register

| Run | Scenario | Status | Evidence classification | Confidence | Reason |
|---|---|---|---|---|---|
| `20260818T204828Z-baseline-no-camera-action` | baseline-no-camera-action | RETAINED | OBSERVED | HIGH | Baseline collection completed; no target camera events normalized in the retained interval. |
| `20260818T205636Z-control-a-no-chatgpt` | control-a-no-chatgpt | INVALID_CONTROL | OBSERVED | HIGH | ChatGPT Classic PID 7924 was present in both process snapshots. Unified Log independently identifies `ChatGPT Classic[7924]`. This run must not be used as a no-ChatGPT negative control. |
| `20260818T210912Z-control-a-no-chatgpt` | control-a-no-chatgpt | VALID_CONTROL | OBSERVED | HIGH | No ChatGPT Classic PID was present before or after the 20-second collection window; process snapshots contained no ChatGPT Classic line; collector marked `control_valid=true`; evidence integrity passed; normalized target-event count was zero. |
| `20260818T211158Z-control-positive-known-camera-capture` | control-positive-known-camera-capture | INCONCLUSIVE_CONTROL | OBSERVED | HIGH | Collection and evidence integrity succeeded, but no retained artifact demonstrates that FaceTime or QuickTime entered active camera capture during the window. ChatGPT Classic PID 1576 was also active, so the run is unsuitable as a clean positive camera control. |
| `20260818T214035Z-quicktime-a2-post-preview` | quicktime-a2-post-preview | INVALID_CONTROL | OBSERVED | HIGH | The AppleScript intended to close the QuickTime movie-recording preview failed with AppleScript error -2741 before this run. Therefore the required post-preview condition was not established and this run is excluded from A/B/A causal comparison. |
| `20260818T214414Z-quicktime-a2-valid-idle-after-preview` | quicktime-a2-valid-idle-after-preview | VALID_CONTROL | OBSERVED | HIGH | QuickTime Player remained running in an idle state after a clean quit and relaunch; no matching `CMIOExtensionStream` activity was observed during the 20-second control window; evidence integrity passed. |
## Interpretation rule

An invalid control is retained as evidence of what occurred but excluded from
comparative inference for the condition it failed to satisfy.

No absence of camera events is interpreted as proof that camera-related code
did not execute. Unified Log observability is incomplete by design.
