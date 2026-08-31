# Sanitized Terraform Plan Gate

This gate produces a bounded, secret-free summary of an explicitly authorized
Proxmox Terraform plan. It does not run `terraform apply`, retain the binary or
raw JSON plan, prove deployment, or demonstrate operating effectiveness.

## Safety boundary

- An operator must explicitly set `ALLOW_PROXMOX_PLAN=YES`.
- The endpoint must use HTTPS inside `10.10.70.0/28`.
- TLS verification must remain enabled.
- Credentials enter through `TF_VAR_*`, are copied into a protected temporary
  JSON variable file, removed from the child environment and bound to the plan
  with an explicit highest-precedence `-var-file` argument.
- Terraform data, the binary plan and raw JSON are created with restrictive
  permissions in a temporary directory and deleted on exit.
- Refresh is disabled to avoid turning this gate into state reconciliation.
- Only the two declared VM resources are accepted.
- Delete, replace, unexpected, duplicate and missing resources fail closed.
- Local `terraform.tfvars` and `*.auto.tfvars` files cannot override the
  endpoint, token identity, target node or TLS setting authorized by the gate.
- Output contains only resource addresses, actions, counts and the claim limit.

Even with refresh disabled, the provider may contact the Proxmox API. Do not
run the gate without separate authorization for the exact endpoint and token.

## Authorized execution template

Export the four required `TF_VAR_*` values through a secure local mechanism,
confirm `TF_VAR_proxmox_tls_insecure=false`, then invoke:

```bash
ALLOW_PROXMOX_PLAN=YES tools/terraform/run_sanitized_plan.sh
```

Do not paste secrets into shell history, CI configuration, issues, pull
requests or retained evidence. Review the secret-free stdout before deciding
whether it may be persisted. Any later `apply` requires a separate gate.

## Offline regression validation

```bash
python3 -m unittest discover \
  -s tests \
  -p 'test_terraform_*.py' \
  -v
bash -n tools/terraform/run_sanitized_plan.sh
```

The regression suite contains bounded positive validation and negative cases
for delete, replace, unexpected, missing and malformed plan content, plus a
Terraform CLI precedence regression with conflicting automatic variable files.
It does not contact Proxmox.
