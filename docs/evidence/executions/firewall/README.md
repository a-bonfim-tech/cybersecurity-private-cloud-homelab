# Reference nftables firewall execution evidence

## Result

Seven bounded synthetic TCP tests executed successfully in an isolated Docker
Desktop harness on 2026-08-13. Connection results and named nftables counters
jointly validate the routed reference-policy behavior:

- `FW-EXEC-001` and `FW-EXEC-002`: explicit allow paths;
- `FW-EXEC-003` and `FW-EXEC-004`: explicit `FW-004` deny paths;
- `FW-EXEC-005` and `FW-EXEC-006`: `FW-005` default-deny paths;
- `FW-NEG-001`: port-scoping regression (`22` allowed, `23` denied).

The firewall container used `--cap-drop ALL`, added only `NET_ADMIN` and
`NET_RAW`, and did not use privileged mode. Four Docker internal bridge
networks represented the TRUSTED, SERVERS, CYBER_LAB and MONITORING zones.
The four synthetic test hosts added only `NET_ADMIN` for route and tunnel
configuration. IP-in-IP links were required because Docker Desktop blocks
ordinary cross-bridge frames before they reach a router container; the inner
policy-addressed packets traversed the nftables forward hook.

## Toolchain observed

- base: `alpine@sha256:14358309a308569c32bdc37e2e0e9694be33a9d99e68afb0f5ff33cc1f695dce`
- nftables: `1.1.3`
- iproute2: `6.15.0`
- tcpdump: `4.99.5`
- Bash: `5.2.37`
- jq: `1.8.1`
- OpenBSD netcat package: `1.229.1-r0`

## Evidence boundary

This is `EXECUTED_SYNTHETIC_TEST_EVIDENCE` for
`REFERENCE_POLICY_ENFORCEMENT`. Counter evidence was observed; kernel logging
was not retained. The execution does not prove pfSense or Proxmox deployment,
production readiness, compliance or operating control effectiveness. The
preventive firewall, Suricata and Wazuh evidence were generated in separate
harnesses and form complementary executed control paths, not one unified
deployed packet path.

Dynamic firewall reproduction in GitHub Actions is not implemented because
granting network-administration capabilities to a hosted runner is not
justified. CI validates the harness structure without those capabilities.

`REFERENCE_LAB_CLEANUP_VERIFIED=true`: all five `hl-*` containers and all four
`hl-*` networks were removed after execution.
