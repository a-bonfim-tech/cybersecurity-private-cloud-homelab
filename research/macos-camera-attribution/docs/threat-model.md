# Threat Model — macOS Camera Attribution Research

## Assets

- camera-generated image data;
- microphone/audio data;
- user privacy;
- TCC authorization state;
- provenance of forensic evidence;
- target-process identity;
- experiment integrity.

## Trust boundaries

1. Application process to macOS media frameworks
2. Application/helper process to CoreMediaIO
3. CoreMediaIO to camera provider services
4. Camera provider to hardware / ISP
5. Application to network stack
6. Local evidence collector to stored forensic artifacts

## Relevant threats

### Spoofing

PID reuse or incomplete process attribution may incorrectly associate an event
with the target application.

Mitigation: retain PID, executable, bundle metadata, process listing,
timestamps and code-signing metadata within each run.

### Tampering

Raw evidence could be modified after acquisition.

Mitigation: run-local SHA-256 manifest and separation of raw and derived data.

### Repudiation

A conclusion could become detached from its supporting command or artifact.

Mitigation: provenance manifest stores acquisition command, run ID and hash.

### Information disclosure

Raw logs may contain usernames, paths, identifiers or network metadata.

Mitigation: raw runs remain excluded from Git until sanitized.

### Denial of service

Aggressive tracing could perturb the system being measured.

Mitigation: bounded native collection and no disabling of platform controls.

### Elevation of privilege

Research must not weaken TCC, SIP or platform security merely to make an
experiment easier.

Mitigation: explicit prohibition on TCC database modification, TCC bypass and
SIP disabling.
