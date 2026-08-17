# S2 FreeBSD Router — PF Segmentation Baseline

Date: 2026-08-17

## Network

- vtnet1: 10.10.10.1/27 — users
- vtnet2: 10.10.20.1/24 — servers
- vtnet3: 10.10.60.1/25 — monitoring
- vtnet4: 10.10.70.1/28 — management
- IPv4 forwarding: enabled
- PF: enabled
- NAT: enabled for all four internal networks

## Observed validation

| Source | Destination | Expected | Observed |
|---|---|---:|---:|
| Monitoring 10.10.60.126 | Users 10.10.10.10 ICMP | ALLOW | PASS |
| Monitoring 10.10.60.126 | Servers 10.10.20.15 ICMP | ALLOW | PASS |
| Monitoring 10.10.60.126 | Servers 10.10.20.15 TCP/22 | ALLOW | PASS |
| Monitoring 10.10.60.126 | Management 10.10.70.1 ICMP | DENY | BLOCK |
| Management 10.10.70.14 | Users 10.10.10.10 ICMP | ALLOW | PASS |
| Management 10.10.70.14 | Servers 10.10.20.15 ICMP | ALLOW | PASS |
| Management 10.10.70.14 | Monitoring 10.10.60.15 ICMP | ALLOW | PASS |
| Users 10.10.10.30 | Servers 10.10.20.15 ICMP | DENY | BLOCK |
| Users 10.10.10.30 | Servers 10.10.20.15 TCP/22 | DENY | BLOCK |
| Monitoring 10.10.60.126 | Internet 1.1.1.1 | ALLOW/NAT | PASS |
| Management 10.10.70.14 | Router 10.10.70.1 TCP/22 | ALLOW | PASS |

## Persistence

Post-reboot observations:

- PF returned Enabled.
- IPv4 forwarding returned enabled.
- sshd returned enabled and listening on TCP/22.
- PF ruleset reloaded automatically.
- Four NAT rules reloaded automatically.
- Management SSH recovered after service initialization.
- Positive and negative smoke tests remained correct.

## Evidence classification

Status: observed  
Confidence: high

## Approved baseline

The segmentation baseline was functionally validated after reboot.
Changes to `/etc/pf.conf` should be treated as controlled changes and should rerun the allow/deny test matrix.
