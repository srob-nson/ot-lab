#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

suffix="$$-$RANDOM"
network="ot-lab-client-failure-test-$suffix"

cleanup() {
  docker network rm "$network" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker build -q -t ot-lab-modbus-hmi-failure-test ./modbus/hmi >/dev/null
docker build -q -t ot-lab-modbus-engineering-failure-test \
  ./modbus/engineering-workstation >/dev/null
docker build -q -t ot-lab-bacnet-bms-failure-test ./bacnet/client >/dev/null
docker build -q -t ot-lab-bacnet-operator-failure-test \
  ./bacnet/operator-workstation >/dev/null
docker build -q -t ot-lab-enip-scanner-failure-test ./enip/client >/dev/null
docker build -q -t ot-lab-enip-process-failure-test \
  ./enip/process-workstation >/dev/null
docker network create --subnet 10.24.0.0/24 "$network" >/dev/null

expect_failure() {
  local role=$1
  shift
  set +e
  "$@" >/dev/null 2>&1
  local status=$?
  set -e
  if [ "$status" -eq 0 ]; then
    printf '%s returned success when its protocol target was unavailable\n' "$role" >&2
    return 1
  fi
}

expect_failure "Modbus HMI" \
  docker run --rm --network "$network" --ip 10.24.0.11 \
  -e MODBUS_PLC_ADDRESS=10.24.0.10 -e OTLAB_CYCLES=1 \
  ot-lab-modbus-hmi-failure-test
expect_failure "Modbus engineering workstation" \
  docker run --rm --network "$network" --ip 10.24.0.12 \
  -e MODBUS_PLC_ADDRESS=10.24.0.10 -e OTLAB_CYCLES=1 \
  ot-lab-modbus-engineering-failure-test
expect_failure "BACnet BMS" \
  docker run --rm --network "$network" --ip 10.24.0.21 \
  -e BACNET_ADDRESS=10.24.0.21 -e BACNET_DEVICE_ADDRESS=10.24.0.20 \
  -e BACNET_DEVICE_INSTANCE=2421 -e OTLAB_CYCLES=1 \
  ot-lab-bacnet-bms-failure-test
expect_failure "BACnet operator workstation" \
  docker run --rm --network "$network" --ip 10.24.0.22 \
  -e BACNET_ADDRESS=10.24.0.22 -e BACNET_DEVICE_ADDRESS=10.24.0.20 \
  -e BACNET_DEVICE_INSTANCE=2422 -e OTLAB_CYCLES=1 \
  ot-lab-bacnet-operator-failure-test
expect_failure "EtherNet/IP scanner" \
  docker run --rm --network "$network" --ip 10.24.0.31 \
  -e ENIP_DEVICE_ADDRESS=10.24.0.30 -e OTLAB_CYCLES=1 \
  ot-lab-enip-scanner-failure-test
expect_failure "EtherNet/IP process workstation" \
  docker run --rm --network "$network" --ip 10.24.0.32 \
  -e ENIP_DEVICE_ADDRESS=10.24.0.30 -e OTLAB_CYCLES=1 \
  ot-lab-enip-process-failure-test

echo "finite client runs report unavailable protocol targets"
