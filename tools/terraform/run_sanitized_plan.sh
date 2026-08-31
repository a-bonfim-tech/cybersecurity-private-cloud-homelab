#!/usr/bin/env bash
set -euo pipefail

# This command may contact the explicitly supplied Proxmox endpoint. It never
# runs terraform apply and retains only the validator's secret-free stdout.
if [[ "${ALLOW_PROXMOX_PLAN:-}" != "YES" ]]; then
  echo "TERRAFORM_PLAN=BLOCKED: set ALLOW_PROXMOX_PLAN=YES after explicit authorization" >&2
  exit 2
fi

required_variables=(
  TF_VAR_proxmox_api_url
  TF_VAR_proxmox_api_token_id
  TF_VAR_proxmox_api_token_secret
  TF_VAR_target_node
)
for variable in "${required_variables[@]}"; do
  if [[ -z "${!variable:-}" ]]; then
    echo "TERRAFORM_PLAN=BLOCKED: missing ${variable}" >&2
    exit 2
  fi
done

if [[ "${TF_VAR_proxmox_tls_insecure:-false}" != "false" ]]; then
  echo "TERRAFORM_PLAN=BLOCKED: TLS verification must remain enabled" >&2
  exit 2
fi

if [[ ! "${TF_VAR_proxmox_api_url}" =~ ^https://10\.10\.70\.([1-9]|1[0-4]):8006/api2/json$ ]]; then
  echo "TERRAFORM_PLAN=BLOCKED: endpoint is outside the restricted management network" >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
terraform_root="${repo_root}/iac/terraform"
umask 077
temporary_root="$(mktemp -d)"
trap 'rm -rf "${temporary_root}"' EXIT

export TF_DATA_DIR="${temporary_root}/terraform-data"
plan_file="${temporary_root}/bounded.tfplan"
plan_json="${temporary_root}/bounded.json"
authorized_vars_file="${temporary_root}/authorized.auto.tfvars.json"

python3 "${repo_root}/tools/terraform/write_authorized_tfvars.py" \
  "${authorized_vars_file}" >/dev/null

# Terraform automatically loads local tfvars with higher precedence than
# TF_VAR_* environment values. Remove the lower-precedence copies after the
# protected explicit file has been created so the checked values have one
# authoritative path into Terraform.
unset TF_VAR_proxmox_api_url
unset TF_VAR_proxmox_api_token_id
unset TF_VAR_proxmox_api_token_secret
unset TF_VAR_proxmox_tls_insecure
unset TF_VAR_target_node

terraform -chdir="${terraform_root}" init -backend=false -input=false >/dev/null
terraform -chdir="${terraform_root}" plan \
  -refresh=false \
  -input=false \
  -lock=false \
  -var-file="${authorized_vars_file}" \
  -out="${plan_file}" >/dev/null
terraform -chdir="${terraform_root}" show -json "${plan_file}" > "${plan_json}"
python3 "${repo_root}/tools/terraform/validate_plan_json.py" "${plan_json}"
