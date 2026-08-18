# QuickTime Camera Attribution — A/B/A Experimental Conclusion

## Status

**Experimental phase: COMPLETE**

The controlled QuickTime A/B/A experiment produced a reproducible
difference in observable CoreMediaIO provider activity.

## Runs

| Condition | Run ID | Validity |
|---|---|---|
| A — QuickTime idle, no preview | `20260818T213549Z-quicktime-a-idle-no-preview` | VALID |
| B — QuickTime movie preview active | `20260818T213817Z-quicktime-b-preview-active` | VALID |
| A2 — attempted post-preview control | `20260818T214035Z-quicktime-a2-post-preview` | INVALID CONTROL |
| A2 — clean idle after preview | `20260818T214414Z-quicktime-a2-valid-idle-after-preview` | VALID |

The first A2 run is excluded from causal comparison because the
AppleScript intervention intended to close the movie-recording preview
failed with error `-2741`.

## Observed A/B/A result

| Signal | A idle | B preview | A2 idle |
|---|---:|---:|---:|
| `ConnectClient` | 0 | 0 | 0 |
| `PowerOnCamera` | 0 | 0 | 0 |
| `PowerOffCamera` | 0 | 0 | 0 |
| `StartStream` | 0 | 0 | 0 |
| `StopStream` | 0 | 0 | 0 |
| client-streaming property | 0 | 0 | 0 |
| frame-duration property | 0 | 0 | 0 |
| `CMIOExtensionStream` activity | 0 | 30 | 0 |
| explicit frame-delivery evidence | 0 | 0 | 0 |

## Finding

**Classification:** supported<br>
**Confidence:** high

Within this controlled observation, activation of the QuickTime movie
preview is associated with repeated `appleh13camerad` CoreMediaIO
`CMIOExtensionStream` activity.

The distinguishing signal appears in the preview condition and is absent
from both idle controls:

`0 -> 30 -> 0`

This A/B/A pattern materially reduces the likelihood that the observed
signal is merely persistent background activity.

## What is directly observed

The following facts are directly supported by collected evidence:

1. QuickTime Player was present during all three valid conditions.
2. The idle A condition contained zero matching `CMIOExtensionStream`
   events.
3. The preview B condition contained 30 matching
   `CMIOExtensionStream` events.
4. The valid post-preview A2 condition contained zero matching
   `CMIOExtensionStream` events.
5. The relevant events in B were emitted by `appleh13camerad`.
6. All three valid runs passed module evidence-integrity validation.
7. Repository-level evidence-integrity validation passed.

## What is NOT established

The experiment does **not** directly establish:

- `PowerOnCamera`;
- `PowerOffCamera`;
- `StartStream`;
- `StopStream`;
- explicit video-frame delivery;
- `CMSampleBuffer` or `CVPixelBuffer` delivery;
- direct process-to-frame attribution;
- proof that QuickTime itself received a particular frame;
- a general macOS API guarantee that the observed private/provider
  message always means active frame delivery.

Therefore the observed `CMIOExtensionStream` messages MUST NOT be
normalized or described as `video_frame_delivered`.

## Attribution boundary

The strongest defensible statement is:

> In this A/B/A experiment, enabling QuickTime Player's movie preview
> was associated with repeated CoreMediaIO stream-related activity in
> `appleh13camerad`; that activity disappeared in the subsequent idle
> control.

The evidence supports **preview-associated camera-provider activity**.

It does not independently prove **frame delivery to QuickTime**.

## Integrity

Validation results:

- A: `MACOS_EVIDENCE_INTEGRITY=PASS`
- B: `MACOS_EVIDENCE_INTEGRITY=PASS`
- A2: `MACOS_EVIDENCE_INTEGRITY=PASS`
- repository: `EVIDENCE_INTEGRITY=PASS`
- final A/B/A: `FINAL_ABA_EVIDENCE_INTEGRITY=PASS`

Repository validation reported:

- evidence IDs: 18
- manifest hashes: 32
- SHA-256 files: 4
- SHA-256 entries: 25
- JSON files: 8
- JSONL files: 3

## Final experimental disposition

**COMPLETE WITH EVIDENCE BOUNDARY**

No additional experiment is required to establish the narrow finding
above.

A separate experiment would be required before making stronger claims
about frame delivery, hardware power state, or end-consumer attribution.
