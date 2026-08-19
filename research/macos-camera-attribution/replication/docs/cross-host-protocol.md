# macOS Camera Attribution — Cross-Host Replication Protocol

## Purpose

Test whether the previously observed A1/B/A2 pattern replicates on an
independent physical Mac without changing the experimental implementation
after observing the second-host result.

## Frozen baseline

The replication implementation must be executed from:

- tag: `macos-camera-attribution-replication-v2`
- commit: `a0f1ff4264879fe630da047d0ec45762f0fd2dd0`

No source-code modification is permitted between baseline verification and
experimental execution.

## Evidence boundary

The primary observable is:

`CMIOExtensionStream`

The experiment may support a claim of provider stream-related activity.

It does not establish direct frame delivery to QuickTime Player and must not
be represented as proof that QuickTime received or consumed video frames.

## Independence requirement

A valid cross-host replication requires a physically distinct Mac.

A second checkout, worktree, user account, shell session, filesystem location,
or virtual environment on the original Mac does not constitute an independent
host.

The second host must produce a pseudonymous host ID distinct from the original
host ID.

Original host ID:

`d2c70c9a2614`

## Experimental sequence

The frozen runner executes:

1. A1 — idle control
2. B — QuickTime movie-preview condition
3. A2 — post-preview idle control

The three run directories must be distinct.

## Primary replication criterion

A full replication requires:

- A1 observable count = 0
- B observable count > 0
- A2 observable count = 0
- outcome = `REPLICATED`
- final replication validation = PASS

The validator remains authoritative for the encoded outcome.

## Result identity

Each execution must produce a result under:

`replication/results/<host_id>/<execution_id>.json`

The result must bind:

- schema version
- execution ID
- host ID
- A1 run
- B run
- A2 run
- observed counts
- outcome
- claim boundary

Historical result files must not be overwritten.

## Evidence handling

Raw evidence is local-review material.

Files under run `raw/` must not be committed to Git.

Permitted repository evidence is limited to explicitly reviewed,
sanitized, derived, or manifest artifacts according to repository policy.

## Second-host preconditions

Before running:

- verify macOS
- record macOS product version and build
- record architecture
- record hardware model and chip
- verify repository commit
- verify exact replication tag
- run static/unit tests
- verify no source modifications

## Interpretation

Possible outcomes:

### REPLICATED

A1 = 0, B > 0, A2 = 0.

Supports cross-host reproducibility of the bounded observable.

### PARTIALLY_REPLICATED

B exceeds both controls, but one or both controls are non-zero.

Requires investigation before broadening the claim.

### NOT_REPLICATED

The expected condition contrast is absent.

This result must be retained. It must not be discarded solely because it
contradicts the original host.

## Anti-bias rule

Do not modify:

- log predicates
- observable definition
- counting logic
- scenario definitions
- timing
- outcome thresholds

after inspecting the second-host result.

Any revised experiment must receive a new protocol/version and be reported
separately.

## Cross-host advancement criterion

The project may describe the behavior as independently replicated only after
a physically distinct Mac:

1. runs the frozen baseline;
2. obtains a distinct host ID;
3. completes A1/B/A2;
4. passes result validation;
5. preserves the evidence boundary;
6. retains the result regardless of outcome.
