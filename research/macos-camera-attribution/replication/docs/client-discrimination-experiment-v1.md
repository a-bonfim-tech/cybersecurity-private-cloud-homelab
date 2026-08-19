# macOS Camera Client Discrimination Experiment v1

## Protocol

This experiment instantiates:

macOS Camera Client Discrimination Protocol v1

Protocol commit:

de24cb7

## Host

Reference host only.

This experiment evaluates client discrimination on the existing host.
It does not establish cross-host reproducibility.

## Frozen conditions

### A — idle

No active camera preview in QuickTime Player or Photo Booth.

### B — QuickTime

Application:

QuickTime Player

Condition:

New Movie Recording preview active.

### C — Photo Booth

Application:

Photo Booth

Bundle identifier:

com.apple.PhotoBooth

Condition:

Photo Booth camera preview active.

## Primary observable

CMIOExtensionStream provider activity.

## Candidate attribution evidence

Only directly observed evidence may be used:

- client PID;
- process identity;
- ConnectClient PID;
- TCC requesting/accessing/responsible process;
- bundle identifier;
- another directly recorded client identifier.

No identifier may be inferred solely from temporal proximity.

## Required comparison

The experiment must determine whether B and C can be distinguished using
client-specific evidence retained by the collection pipeline.

Provider activity alone is insufficient for client discrimination.

## Outcome

CLIENT_DISCRIMINATION_SUPPORTED

Only if a directly observed and repeatable client-specific discriminator
separates B from C.

PROVIDER_ONLY

If camera/provider activity separates active conditions from idle but does
not reliably distinguish QuickTime from Photo Booth.

INCONCLUSIVE

If evidence is incomplete, contradictory, unstable, or otherwise
insufficient.

## Evidence boundary

This experiment does not establish:

- direct frame delivery;
- frame consumption;
- ownership of every CMIOExtensionStream event;
- cross-host reproducibility.

## Anti-bias freeze

After the first A/B/C collection begins, do not modify:

- client selection;
- observable;
- predicates;
- normalizer behavior;
- discriminator criteria;
- timing;
- outcome definitions.

Any revision requires Experiment v2.
