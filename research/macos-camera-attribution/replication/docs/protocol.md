# macOS Camera Attribution — Replication Protocol

## Objective

Evaluate whether the previously observed A/B/A association is reproducible
on another macOS host and/or macOS version.

Baseline reference:

- commit: `782acaf`

The baseline result is not modified by replication outcomes.

## Experimental sequence

Each host MUST execute:

1. A1 — QuickTime Player running, no movie-recording preview.
2. B — QuickTime Player movie-recording preview active.
3. A2 — QuickTime Player cleanly terminated, relaunched, idle, no preview.

Recommended retained observation window:

- A1: 20 seconds
- B: 30 seconds
- A2: 20 seconds

## Required controls

The experiment MUST record:

- QuickTime PID before and after each run;
- macOS product version and build;
- hardware model;
- raw Unified Log locally;
- raw process snapshots locally;
- derived artifacts separately;
- evidence integrity result.

A2 is invalid unless the preview condition was actually removed before
collection.

## Primary observable

Primary comparison:

`CMIOExtensionStream`-matching provider activity in `appleh13camerad`.

Expected baseline pattern:

`A1 -> B -> A2 = 0 -> elevated -> 0`

Exact event counts are NOT required to match the original host.

## Evidence boundary

The following MUST NOT be inferred solely from `CMIOExtensionStream`:

- frame delivery;
- CMSampleBuffer delivery;
- CVPixelBuffer delivery;
- camera hardware power state;
- direct frame attribution to QuickTime Player;
- direct proof that QuickTime consumed a particular frame.

## Classification

Replication outcome:

- REPLICATED:
  B > A1 and B > A2, with A1/A2 free of matching activity.
- PARTIALLY_REPLICATED:
  B shows stronger activity, but controls contain ambiguous activity.
- NOT_REPLICATED:
  no meaningful difference between A1, B and A2.
- INVALID:
  experimental condition, collection, or integrity requirement failed.

## Repository policy

Raw host evidence MUST remain outside Git.

Git may contain:

- sanitized host metadata;
- manifests;
- derived timelines;
- derived manifests;
- aggregate comparison results;
- protocol and conclusions.

