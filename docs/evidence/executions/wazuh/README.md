# Wazuh-native rule-test evidence

`WAZUH-EXEC-001` uses the canonical single-line representation of the actual
Suricata `SURICATA-EXEC-001` alert. Semantic equality with the retained source
event was verified using canonical JSON ordering before execution.

The test ran with Wazuh `4.14.7` in the official manager image fixed by OCI
index digest `sha256:c364ef100ba40d501537b1668a5a72bba4c4fbcf39bbef6a02123ff221fc40d0`.
The local ARM64 platform digest was
`sha256:e38431e7420cffd3a2abd0a9c8d8292e4f646be5c718213c1c15201076a1920f`.

The native assertion `100010:7:json` returned exit code `0`. Two deterministic
negative inputs did not match rule `100010`. The result proves bounded decoder
and rule behavior, not manager operation, alert persistence, firewall
enforcement or control effectiveness.
