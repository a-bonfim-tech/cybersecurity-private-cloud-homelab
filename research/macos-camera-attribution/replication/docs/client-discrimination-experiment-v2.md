# macOS Camera Client Discrimination Experiment v2

## Purpose

Determine whether retained macOS camera evidence can distinguish provider
activity associated with QuickTime Player from provider activity associated
with Photo Booth.

The experiment does not claim direct frame delivery.

## Reason for v2

Experiment v1 allowed execution to continue without proving that its A, B,
and C conditions were operationally valid.

Execution 20260819T113929Z demonstrated this defect:

- A contained provider activity;
- B lacked positive provider activity;
- C lacked positive provider activity.

That execution is retained as INVALID_CONDITION_CONTRAST and must not be
used to support or reject client discrimination.

## Frozen clients

B:

- application: QuickTime Player
- bundle identifier: com.apple.QuickTimePlayerX
- required state: movie-recording document open with preview active

C:

- application: Photo Booth
- bundle identifier: com.apple.PhotoBooth
- required state: Photo Booth camera preview active

## Observable

CMIOExtensionStream activity emitted by appleh13camerad.

Provider activity alone is not a client discriminator.

## Condition A — idle

Required before collection:

- QuickTime has zero movie-recording documents;
- Photo Booth is not camera-active;
- CMIOExtensionStream count is zero in a clean 5-second window.

Application processes may exist.

If any required condition fails, abort with:

ABORTED_CONDITION_INVALID

Do not collect A as valid.

## Condition B — QuickTime

Required before collection:

- QuickTime Player process exists;
- QuickTime reports at least one movie-recording document;
- Photo Booth is not camera-active;
- CMIOExtensionStream activity is positive in the immediate precheck window.

If any required condition fails, abort with:

ABORTED_CONDITION_INVALID

Do not collect B as valid.

## Transition B to C

Before C:

- close every QuickTime movie-recording document;
- verify QuickTime document count is zero;
- establish a clean provider window with zero CMIOExtensionStream activity.

The QuickTime application process itself may remain running.

## Condition C — Photo Booth

Required before collection:

- Photo Booth process exists;
- System Events reports bundle identifier com.apple.PhotoBooth;
- QuickTime movie-recording document count is zero;
- CMIOExtensionStream activity is positive in the immediate precheck window.

If any required condition fails, abort with:

ABORTED_CONDITION_INVALID

Do not collect C as valid.

## Valid contrast

An execution is eligible for client-discrimination analysis only when all
three gates passed:

A:
CMIOExtensionStream = 0

B:
QuickTime movie-recording document active and CMIOExtensionStream > 0

C:
Photo Booth identity observed, QuickTime document count = 0, and
CMIOExtensionStream > 0

## Client discrimination

CLIENT_DISCRIMINATION_SUPPORTED requires a directly observed,
client-specific discriminator that separates B from C.

Examples may include:

- explicit client PID in provider evidence;
- directly logged process identity;
- explicit client connection record;
- stable, evidence-backed TCC/process/provider linkage.

Temporal proximity alone is insufficient.

## Outcomes

CLIENT_DISCRIMINATION_SUPPORTED

Valid A/B/C contrast plus directly observed, repeatable client discriminator.

PROVIDER_ONLY

Valid A/B/C contrast exists, but retained evidence does not discriminate
QuickTime from Photo Booth.

INCONCLUSIVE

Valid conditions were collected but evidence is contradictory or otherwise
insufficient.

ABORTED_CONDITION_INVALID

One or more experimental conditions failed their frozen precollection gate.

An aborted execution is operational evidence, not a discrimination result.

## Claim boundary

CMIOExtensionStream remains provider stream-related activity only; not direct
frame-delivery evidence.

Do not infer:

- direct frame delivery;
- application frame consumption;
- ownership of every provider event;
- client causality from timing alone;
- cross-host reproducibility.

## Anti-bias freeze

After the first v2 A/B/C execution begins, do not change:

- clients;
- observable;
- gate definitions;
- log predicates;
- timing windows;
- normalization rules;
- discriminator rules;
- classification thresholds.

Any such change requires experiment v3.
