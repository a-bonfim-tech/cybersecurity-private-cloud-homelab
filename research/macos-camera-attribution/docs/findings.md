# Findings

## MACCAM-001 — Camera provider interaction attributed to target process

**Status:** OPEN<br>
**Evidence classification:** OBSERVED<br>
**Confidence:** HIGH for the log event; lower for interpretations beyond it.

### Observation

Historical investigation output contains CoreMediaIO / camera-provider activity
attributed to ChatGPT Classic process instances, including `ConnectClient`
events.

### Interpretation

This establishes provider interaction when supported by retained source
evidence.

It does not independently establish video-frame delivery.

### Alternative explanations

Device discovery, capability probing, preview preparation, preference
resolution, or other initialization paths may produce provider interactions.

### Required evidence for stronger conclusion

Compare against a known positive camera consumer and identify artifacts that
are specific to active capture rather than enumeration.

---

## MACCAM-002 — Camera hardware/ISP power transition

**Status:** OPEN<br>
**Evidence classification:** OBSERVED<br>
**Confidence:** HIGH for the hardware power event.

### Observation

Historical logs contain `PowerOnCamera` / `ISP_PowerOnCamera` and later
power-off events temporally near camera-provider activity.

### Interpretation

The camera ISP became powered.

### Limitation

ISP power state is not proof that frames were delivered to the target process.

---

## MACCAM-003 — Actual video-frame consumption

**Status:** HYPOTHESIS<br>
**Evidence classification:** UNSUPPORTED by currently retained project evidence<br>
**Confidence:** LOW

No retained evidence currently demonstrates delivery of video frames to
ChatGPT Classic.

Required experiment: positive-control discrimination followed by equivalent
measurement of the target application.

---

## MACCAM-004 — Video exfiltration

**Status:** HYPOTHESIS<br>
**Evidence classification:** UNSUPPORTED<br>
**Confidence:** LOW

Network activity alone cannot establish transmission of camera-derived data.

A stronger conclusion requires evidence connecting frame acquisition to the
target process and separately characterizing corresponding network transfer.

---

## MACCAM-005 — QuickTime versus Photo Booth provider contrast

**Status:** CLOSED AT PROVIDER-ONLY BOUNDARY<br>
**Evidence classification:** OBSERVED<br>
**Confidence:** HIGH for the gated provider observations.

Execution `20260820T045446Z` passed the frozen v2 gates with idle provider
count `0`, QuickTime provider count `5`, an idle B-to-C transition, and Photo
Booth provider count `7`.

This is a valid A/B/C provider-level contrast. The retained evidence contains
no direct, repeatable client/provider discriminator separating QuickTime from
Photo Booth. The final classification is `PROVIDER_ONLY`, not
`CLIENT_DISCRIMINATION_SUPPORTED`.

Mandatory boundary: **Provider stream-related activity only; not direct
frame-delivery evidence.**
