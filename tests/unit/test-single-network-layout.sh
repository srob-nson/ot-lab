#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
config_file=$(mktemp)
trap 'rm -f "$config_file"' EXIT

docker compose --project-directory "$repo_root" \
  -f "$repo_root/compose.yaml" config --format json >"$config_file"

python3 - "$config_file" "$repo_root" <<'PY'
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
repo_root = Path(sys.argv[2]).resolve()
config = json.loads(config_path.read_text())

expected = {
    "modbus-plc": ("modbus/server", "10.20.0.10"),
    "modbus-client": ("modbus/hmi", "10.20.0.11"),
    "modbus-engineering": ("modbus/engineering-workstation", "10.20.0.12"),
    "bacnet-plc": ("bacnet/device", "10.20.0.20"),
    "bacnet-client": ("bacnet/client", "10.20.0.21"),
    "bacnet-operator": ("bacnet/operator-workstation", "10.20.0.22"),
    "enip-device": ("enip/device", "10.20.0.30"),
    "enip-client": ("enip/client", "10.20.0.31"),
    "enip-process": ("enip/process-workstation", "10.20.0.32"),
}

services = config["services"]
assert set(services) == set(expected), (
    f"expected exactly nine protocol services, got {sorted(services)}"
)

for service_name, (relative_context, address) in expected.items():
    service = services[service_name]
    actual_context = Path(service["build"]["context"]).resolve()
    expected_context = (repo_root / relative_context).resolve()
    assert actual_context == expected_context, (
        f"{service_name} build context is {actual_context}, expected {expected_context}"
    )
    assert (actual_context / "Dockerfile").is_file(), (
        f"{service_name} has no Dockerfile in {actual_context}"
    )
    assert set(service["networks"]) == {"ot"}, (
        f"{service_name} must attach only to ot-net"
    )
    assert service["networks"]["ot"]["ipv4_address"] == address, (
        f"{service_name} address must be {address}"
    )
    assert "cap_add" not in service, f"{service_name} must not require NET_ADMIN"

ot_network = config["networks"]["ot"]
assert ot_network["external"] is True
assert ot_network["name"] == "ot-net"
assert ot_network["ipam"]["config"] == [{"subnet": "10.20.0.0/24"}]

print("single-network layout verified: nine protocol devices on ot-net")
PY
