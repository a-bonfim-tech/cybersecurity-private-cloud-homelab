# macOS Camera Client Discrimination Protocol v1

## Purpose

Determine whether retained macOS camera evidence can distinguish camera
provider activity associated with different client applications.

This protocol does not test or claim direct video-frame delivery.

## Established evidence

Same-host repeatability for CMIOExtensionStream provider activity is already
supported on the reference host.

That finding is not equivalent to application-level attribution.

## Hypothesis

If the available evidence contains stable client-specific identifiers or
causal linkage, QuickTime camera activity should be distinguishable from
camera activity initiated by another client application.

## Conditions

### A — idle control

No camera document or preview is active.

### B — QuickTime

QuickTime Player has an active movie-recording preview.

### C — alternate client

A distinct camera client has an active camera preview.

The alternate client must be selected before inspecting the experimental
logs.

## Primary question

Does the retained evidence expose a stable discriminator linking provider
activity to the initiating client?

Possible discriminators include only fields directly present in evidence,
such as:

- client PID;
- process identity;
- explicit client connection events;
- stable TCC/process linkage;
- another directly observed client identifier.

Absence of such a discriminator must be reported as an unsuccessful
attribution result.

## Claim boundary

CMIOExtensionStream activity remains provider stream-related activity only.

Do not infer:

- direct video-frame delivery;
- frame consumption by an application;
- application ownership of every provider event;
- causal client attribution without an observed linkage.

## Outcome classes

### CLIENT_DISCRIMINATION_SUPPORTED

Evidence contains a repeatable client-specific discriminator that separates
B from C and is absent from A.

### PROVIDER_ONLY

Camera activity is distinguishable from idle, but QuickTime and the alternate
client cannot be reliably distinguished.

### INCONCLUSIVE

The evidence is incomplete, unstable, ambiguous, or internally inconsistent.

## Anti-bias rule

After B and C evidence has been collected, do not change:

- predicates;
- normalization rules;
- discriminator definition;
- matching criteria;
- timing;
- outcome thresholds.

Any revised experiment requires a new protocol version.
