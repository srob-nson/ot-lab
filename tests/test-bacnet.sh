#!/usr/bin/env bash
set -euo pipefail

test_network="ot-lab-bacnet-test-$RANDOM"
device_container="ot-lab-bacnet-device-test-$RANDOM"
client_container="ot-lab-bacnet-client-test-$RANDOM"

cleanup() {
  docker rm -f "$device_container" "$client_container" >/dev/null 2>&1 || true
  docker network rm "$test_network" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker build -q -t ot-lab-bacnet-device-test ./bacnet/device >/dev/null
docker build -q -t ot-lab-bacnet-client-test ./bacnet/client >/dev/null
docker network create --subnet 10.21.0.0/24 "$test_network" >/dev/null
docker run -d --name "$device_container" --network "$test_network" --ip 10.21.0.20 \
  -e BACNET_ADDRESS=10.21.0.20 ot-lab-bacnet-device-test >/dev/null
sleep 2
set +e
docker run --name "$client_container" --network "$test_network" --ip 10.21.0.21 \
  -e BACNET_ADDRESS=10.21.0.21 ot-lab-bacnet-client-test \
  timeout 8 python -u /client.py | grep -F "Discovered BACnet device 2001"
client_statuses=("${PIPESTATUS[@]}")
set -e

if [ "${client_statuses[0]}" -ne 124 ] || [ "${client_statuses[1]}" -ne 0 ]; then
  exit 1
fi

docker run --network "$test_network" --ip 10.21.0.22 \
  -v "$PWD/tests/bacnet-read-write.py:/bacnet-read-write.py:ro" \
  ot-lab-bacnet-client-test python /bacnet-read-write.py
