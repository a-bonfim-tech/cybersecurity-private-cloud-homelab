# Purple-Team Runbook 001: Bounded SYN Reconnaissance Simulation

## Objective
Validate Suricata SID `1000001` and the specified Wazuh correlation rule
`100010` when authorized synthetic SYN traffic originates from VLAN 30 and is
directed toward the controlled VLAN 20 test host.

## Scope and safety

- Synthetic lab networks only: `10.10.30.0/24` and `10.10.20.0/24`.
- No Internet, third-party, production or personal data targets.
- Obtain the lab owner's confirmation before enabling the temporary test path.
- The checked-in PCAP and JSON are `TEST_VECTOR_SPECIFICATION`, not proof that
  this complete procedure was executed.

## Preconditions

1. VLAN 30 source and VLAN 20 target are controlled lab assets.
2. Suricata is installed and SID `1000001` passes configuration validation.
3. A capture interface observes the test path.
4. Wazuh has a JSON decoder path for Suricata EVE data and local rule `100010`.
5. Exact tool versions and UTC start time are recorded before execution.

## Attack Execution

All commands below are `COMMAND_TO_EXECUTE`. They are not recorded as executed
by this repository version.

```bash
# On the authorized capture point:
sudo tcpdump -i <LAB_CAPTURE_INTERFACE> -nn -s 0 -w recon_vlan30_to_vlan20.pcap \
  'src net 10.10.30.0/24 and dst net 10.10.20.0/24 and tcp'

# From the controlled VLAN 30 source; use only the controlled lab target:
nmap -n -Pn -sS -p 22,80,443,8080 --max-retries 1 --host-timeout 30s \
  10.10.20.15
```

Stop the capture immediately after the bounded test.

## Positive test

1. Generate at least eight SYN packets inside ten seconds so the configured
   `detection_filter` can trigger.
2. Validate the resulting PCAP with `capinfos` and `tshark`.
3. Replay the capture through Suricata offline and retain `eve.json`.
4. Forward the Suricata EVE alert through the controlled Wazuh test path.
5. Confirm SID `1000001` and Wazuh rule `100010` without altering their IDs.

## Negative test

Capture benign single-connection traffic from an authorized source or fewer
than eight VLAN 30 SYN packets in ten seconds. Confirm that SID `1000001` does
not alert. Record the negative PCAP and result separately.

## Validation commands

```bash
suricata -T -S detections/suricata/local.rules -c <SURICATA_CONFIG>
capinfos recon_vlan30_to_vlan20.pcap
tshark -r recon_vlan30_to_vlan20.pcap -T fields \
  -e frame.number -e ip.src -e ip.dst -e tcp.dstport -e tcp.flags
suricata -r recon_vlan30_to_vlan20.pcap -S detections/suricata/local.rules \
  -c <SURICATA_CONFIG> -l <OUTPUT_DIRECTORY>
shasum -a 256 recon_vlan30_to_vlan20.pcap <OUTPUT_DIRECTORY>/eve.json
```

## Telemetry & Detection Verification

Populate the evidence manifest only from observed output:

1. Suricata configuration result and exact version.
2. Positive and negative PCAP hashes.
3. Suricata `eve.json` hash and matching SID.
4. Wazuh test output and matching rule ID, if executed.
5. Firewall log with the matching five-tuple, if enforcement is evaluated.

An IDS alert does not prove that the firewall blocked the packet.

## Result classification

- `SPECIFICATION_ONLY`: procedure or test vector exists but was not executed.
- `VALIDATED`: syntax or file structure was checked.
- `EXECUTED_SYNTHETIC_TEST_EVIDENCE`: the procedure ran and retained output.
- `EFFECTIVE`: requires repeatable operating evidence beyond this runbook.

## Cleanup

1. Remove any temporary firewall exception.
2. Stop capture and test processes.
3. Confirm the VLAN 30 default-deny baseline is restored.
4. Remove transient tool output that contains unnecessary host details.
5. Retain only minimized synthetic evidence and its hashes.

## Independent reproduction gate

An independent reviewer must be able to reproduce both tests from recorded
versions, commands and inputs. Until then, the scenario remains
`PENDING_EXECUTION`.
