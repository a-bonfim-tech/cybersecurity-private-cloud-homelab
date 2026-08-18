# Limitations

1. Unified Log is not a complete execution trace.
2. Absence of a particular frame-related log string is not proof that a frame
   was never delivered.
3. Camera hardware power state does not identify the ultimate consumer of a
   frame.
4. CoreMediaIO enumeration is not equivalent to active capture.
5. TCC database rows alone do not describe every runtime attribution path.
6. TCC numeric fields must not be assigned undocumented semantics merely from
   observation.
7. TLS traffic cannot be characterized as video upload solely from timing or
   byte volume.
8. PID values are reusable and require run-local attribution.
9. Private/redacted fields in Apple logs can prevent definitive identity
   reconstruction.
10. macOS behavior may differ across OS builds, application versions and
    hardware.
