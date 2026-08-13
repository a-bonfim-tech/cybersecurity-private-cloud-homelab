# Peer-Trusted Network Persistence Evidence

## Claim under test

The synthetic `peer-trusted` Ubuntu guest retains the approved VLAN 10 host
configuration across a controlled reboot:

- interface `enp0s1`;
- address `10.10.10.10/24`;
- DHCPv4 and DHCPv6 disabled;
- no persistent or runtime default route;
- no persistent or interface-scoped DNS servers.

## Classification and scope

- Evidence ID: `PEER-TRUSTED-NET-EXEC-001`
- Classification: `EXECUTED_SYNTHETIC_TEST_EVIDENCE`
- Execution date: `2026-08-13`
- Asset: local UTM guest `peer-trusted`
- Network scope: synthetic VLAN 10 TRUSTED lab segment only

The test was observed interactively in the local guest console. The retained
artifact is deliberately minimized: it contains configuration facts and
results, but no password, password hash, secret, recovery credential, VM disk
or recovery ISO.

## Observed pre-state

The runtime address was `10.10.10.10/27`. The persistent Netplan source also
used `/27` and contained a default gateway of `10.10.10.1` plus DNS servers
`1.1.1.1` and `8.8.8.8`. The runtime default route was already absent, so the
runtime and persistent pre-state were not equivalent.

Before mutation, the existing source was preserved as:

```text
/etc/netplan/01-segment2-client.yaml.pre-correction-20260813
```

Its presence was verified before the change and again after reboot.

## Applied persistent source

The corrected `/etc/netplan/01-segment2-client.yaml` was verified with mode
`0600` and the following exact content:

```yaml
network:
  version: 2
  ethernets:
    enp0s1:
      dhcp4: false
      dhcp6: false
      addresses:
        - 10.10.10.10/24
```

No gateway or nameserver stanza is present.

## Execution and validation sequence

1. Preserved the pre-change Netplan source as the rollback file.
2. Installed the minimal persistent source shown above.
3. Ran `netplan generate`: `PASS`.
4. Ran `netplan apply`: `PASS`.
5. Verified immediate runtime address `10.10.10.10/24`: `PASS`.
6. Verified no runtime default route: `PASS`.
7. Verified no interface-scoped DNS servers: `PASS`.
8. Performed a controlled reboot: `PASS`.
9. Completed human login validation after boot: `PASS`.
10. Repeated runtime and persistent-source checks: `PASS`.

The machine-readable result is
[`PEER-TRUSTED-NET-EXEC-001-summary.json`](PEER-TRUSTED-NET-EXEC-001-summary.json).

## Evidence boundary

This gate proves only one guest's persistent network configuration and its
post-reboot runtime state. It does **not** prove:

- pfSense configuration or enforcement;
- Proxmox deployment;
- inter-zone reachability or isolation;
- firewall rule behavior;
- Internet isolation beyond the observed absence of route and DNS;
- continuous operation or control effectiveness.

No additional network change, pfSense mutation or other-VM mutation was part
of this retention operation.

```text
PEER_TRUSTED_NETWORK_GATE=PASS
PERSISTENT_CONFIGURATION_VERIFIED=true
POST_REBOOT_PERSISTENCE_VERIFIED=true
PFSENSE_EXECUTION_PROVEN=false
CONTROL_EFFECTIVENESS_CLAIMED=false
```
