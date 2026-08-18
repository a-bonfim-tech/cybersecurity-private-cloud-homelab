# macOS Camera Attribution Evidence

Raw experiment runs are intentionally excluded from Git by default.

Each local execution is stored under:

    evidence/runs/<run-id>/

The collector preserves raw command output and generates SHA-256 provenance.

Do not commit raw workstation evidence until it has been reviewed and sanitized.
Sanitized regression material belongs under `tests/fixtures/`.

Evidence semantics:

- OBSERVED: directly present in an acquired artifact.
- SUPPORTED: corroborated by sufficient indirect evidence.
- INFERRED: reasonable interpretation that is not directly observed.
- HYPOTHESIS: requires an explicit experiment.
- UNSUPPORTED: not sustained by the available evidence.

Confidence is independently expressed as HIGH, MEDIUM, or LOW.
