# Methodology

## Experimental design

The research uses repeatable bounded runs.

Planned scenarios:

| ID | Scenario |
|---|---|
| A | Baseline without target application activity |
| B | Target application launch |
| C | Target application idle |
| D | Voice functionality |
| E | Explicit camera-related application action |
| F | Camera-authorized condition |
| G | Camera-denied condition |
| H | Known positive camera consumer |
| I | Negative control |
| J | Optional network-isolated condition |

The positive control is essential. It provides an empirical reference for the
observable artifacts associated with known video capture on the same macOS
build and hardware.

## Acquisition principles

Collection is:

- bounded in time;
- read-only where technically possible;
- performed with native macOS tools;
- timestamped;
- hashed;
- associated with a unique run ID;
- retained locally until privacy review.

## Interpretation boundary

The following are separate propositions and must not be collapsed:

1. a process enumerated camera devices;
2. a process connected to a camera provider;
3. camera hardware or ISP powered on;
4. a camera stream became active;
5. video frames were delivered to a process;
6. network activity occurred concurrently;
7. video-derived payload was transmitted.

Evidence for one proposition does not automatically establish the next.
