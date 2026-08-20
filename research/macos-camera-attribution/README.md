# macOS Camera Attribution Research

## Research question

What can macOS artifacts establish about camera-related behavior attributed to an
application process, and which artifacts distinguish camera discovery or
initialization from actual video-frame consumption?

The initial target application is ChatGPT Classic (`com.openai.chat`), but the
methodology is deliberately application-agnostic and requires positive and
negative controls.

## Current evidence boundary

Previously observed investigative artifacts include process attribution to
ChatGPT Classic, CoreMediaIO/provider interaction, camera device and format
enumeration, `ConnectClient`, and ISP power transitions.

Those observations do **not** by themselves establish that application code
received video frames.

No claim of TCC bypass or video exfiltration is made without separate evidence.

## Evidence model

Every conclusion uses one of:

- OBSERVED
- SUPPORTED
- INFERRED
- HYPOTHESIS
- UNSUPPORTED

and a separate confidence level:

- HIGH
- MEDIUM
- LOW

## Repository structure

- `tools/collect_run.sh` — bounded read-only macOS acquisition
- `tools/build_manifest.py` — SHA-256 provenance manifest
- `tools/normalize_timeline.py` — normalized event timeline
- `tools/validate_module.py` — integrity and schema checks
- `tests/fixtures/` — sanitized deterministic regression data
- `evidence/runs/` — local raw runs, excluded from Git
- `docs/` — methodology, findings, limitations, threat model and reproduction

## Safety constraints

The tooling does not modify TCC databases, disable SIP, bypass TCC, or weaken
macOS security controls.

Raw workstation evidence is not committed automatically.

## Current conclusion

Repeated same-host A1/B/A2 executions support an association between QuickTime
movie-preview activation and `CMIOExtensionStream` provider activity on one
physical Mac. Cross-host reproducibility remains `NOT_TESTED`.

The v1 QuickTime-versus-Photo Booth execution has an invalid condition
contrast. Ten retained historical v2 attempts are
`ABORTED_CONDITION_INVALID`; an abort is operational evidence, not a
discrimination outcome. A later v2 execution (`20260820T045446Z`) passed all
three condition gates and established provider activity under both active
clients, but no direct client/provider discriminator. Its frozen
classification is `PROVIDER_ONLY`, and it is not usable to claim client
discrimination.

Camera-provider interaction and hardware initialization remain semantically
distinct from demonstrated frame consumption. The mandatory claim boundary is:

> Provider stream-related activity only; not direct frame-delivery evidence.

See the [experiment register](docs/experiment-register.md) and
[cross-host protocol](replication/docs/cross-host-protocol.md).
