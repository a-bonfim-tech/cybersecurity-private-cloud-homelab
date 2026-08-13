# Isolated nftables reference firewall harness

This harness reproduces the routed portions of the four-zone policy in
`docs/governance/firewall-policy.md`. It builds its own digest-pinned Alpine
image, creates four Docker `--internal` networks and applies a default-deny
`nftables` forward chain inside a capability-minimized firewall container.
Because Docker Desktop enforces bridge-to-bridge isolation before an ordinary
router-container next hop can receive the frame, the harness uses one bounded
IP-in-IP link per zone. Auxiliary `.253` firewall and host transport aliases
carry only the encapsulated synthetic packets. The inner packets retain the
policy addresses (`10.10.10.10`, `10.10.20.15`, `10.10.30.5` and
`10.10.40.10`) and traverse the nftables `forward` hook.

## Evidence boundary

The harness produces executed synthetic reference-policy evidence. It does not
prove pfSense or Proxmox deployment, production readiness, compliance or
operating control effectiveness. `FW-003` SPAN/TAP semantics are not applicable
to this routed harness. Kernel firewall logs are not retained; named nftables
counters provide the rule-traversal evidence.

## Execution

Docker Desktop must be running. From the repository root:

```sh
tools/firewall-lab/validate-static.sh
tools/firewall-lab/setup.sh
tools/firewall-lab/test.sh
tools/firewall-lab/cleanup.sh
```

Cleanup is explicit and removes only the five `hl-*` containers and four
`hl-*` networks owned by this harness. Run it after a failed test as well.

## Reference image tools

The retained execution used the digest-pinned Alpine base declared in the
Dockerfile and recorded the observed package/runtime versions in the evidence
README. The image installs only Bash, GNU coreutils, iproute2, jq,
netcat-openbsd, nftables and tcpdump.

Dynamic CI reproduction is intentionally not configured because granting
network-administration capabilities to a hosted runner is not justified. CI
performs the non-privileged static portion with
`SKIP_NFT_IMAGE_PARSE=1`; the retained local evidence covers the bounded
capability-dependent execution.
