# Initial Threat Model (STRIDE)

## Target: Server Zone Ingress
* Spoofing: Mitigated by 802.1Q VLAN Isolation & MAC Filtering
* Tampering: TLS 1.3 enforced on all internal API calls
* Information Disclosure: Strict Network Segmentation
