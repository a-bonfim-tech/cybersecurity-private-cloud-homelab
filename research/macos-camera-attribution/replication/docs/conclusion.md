# Same-host temporal replication conclusion

## Experimental disposition

**REPLICATED WITH EVIDENCE BOUNDARY**

This experiment is a temporal replication on the same physical host as the
original QuickTime A/B/A experiment.

It is not a cross-host replication.

## Replication design

The replicated sequence was:

- A1: QuickTime Player running with zero documents and no movie preview;
- B: QuickTime Player movie-recording preview active;
- A2: QuickTime Player fully quit, relaunched, and running with zero documents.

The primary observable was the number of raw Unified Log lines matching
`CMIOExtensionStream` from camera-provider activity.

## Result

Observed counts:

| Condition | CMIOExtensionStream matches |
|---|---:|
| A1 idle | 0 |
| B preview | 31 |
| A2 idle | 0 |

Observed replication pattern:

`0 -> 31 -> 0`

Independent recomputation from the three raw Unified Log artifacts returned:

`INDEPENDENT_REPLICATION_CHECK=REPLICATED`

## Relationship to original experiment

The original retained experiment produced:

`0 -> 30 -> 0`

The temporal replication produced:

`0 -> 31 -> 0`

The exact count is not treated as a required invariant.

The relevant repeated observation is that provider stream-related activity
appeared during the QuickTime movie-preview condition and was absent from
both idle controls.

## Evidence classification

Finding:

**QuickTime movie-preview activation is associated with repeated
CoreMediaIO provider stream-related activity on this host.**

Classification: **observed**

Confidence: **high for same-host temporal repeatability**

Generalization to other hosts: **not established**

## Claim boundary

This replication does not directly evidence:

- `CMSampleBuffer` delivery;
- `CVPixelBuffer` delivery;
- delivery of a particular video frame;
- receipt of a frame by QuickTime Player;
- camera hardware power state;
- a public macOS API guarantee for the private/provider log message;
- cross-host reproducibility.

The observed `CMIOExtensionStream` message MUST NOT be normalized or
described as `video_frame_delivered`.

## Integrity

Each new run independently passed:

`MACOS_EVIDENCE_INTEGRITY=PASS`

The replication test suite passed all seven normalization tests.

The raw artifacts remain excluded from Git.

The replication metadata privacy scan passed.

The repository-wide `tools/validate_evidence_integrity.py` output retained
its prior repository counts and therefore is not used as proof that these
three new replication runs were incorporated into that validator's global
inventory.

## Final disposition

**SAME_HOST_TEMPORAL_REPLICATION=REPLICATED**

The next evidentiary upgrade requires a second host or a materially different
hardware/macOS configuration.
