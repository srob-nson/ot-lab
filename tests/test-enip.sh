#!/usr/bin/env bash
set -euo pipefail

test_network="ot-lab-enip-test-$RANDOM"
device_container="ot-lab-enip-device-test-$RANDOM"
client_container="ot-lab-enip-client-test-$RANDOM"

cleanup() {
  docker rm -f "$device_container" "$client_container" >/dev/null 2>&1 || true
  docker network rm "$test_network" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker build -q -t ot-lab-enip-device-test ./enip/device >/dev/null
docker build -q -t ot-lab-enip-client-test ./enip/client >/dev/null
docker network create --subnet 10.22.0.0/24 "$test_network" >/dev/null

# The device listens on all interfaces so UDP List Identity broadcasts on this
# Docker bridge reach it. EtherNet/IP uses UDP/44818 for discovery and TCP/44818
# for the tag read/write session.
docker run -d --name "$device_container" --network "$test_network" --ip 10.22.0.30 \
  -e ENIP_DEVICE_ADDRESS=10.22.0.30 ot-lab-enip-device-test >/dev/null
sleep 2

docker run --name "$client_container" --network "$test_network" --ip 10.22.0.31 \
  -e ENIP_DISCOVERY_ADDRESS=10.22.0.255 \
  -e ENIP_DEVICE_ADDRESS=10.22.0.30 \
  -e ENIP_ONCE=1 ot-lab-enip-client-test | tee /tmp/ot-lab-enip-client-test.log

grep -F "Discovered EtherNet/IP device: ENIP-Simulated-PLC" \
  /tmp/ot-lab-enip-client-test.log
grep -F "ProcessValue: 0.0" /tmp/ot-lab-enip-client-test.log

docker run --network "$test_network" --ip 10.22.0.32 \
  -v "$PWD/tests/enip-read-write.py:/enip-read-write.py:ro" \
  ot-lab-enip-client-test python /enip-read-write.py
