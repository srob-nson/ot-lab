#!/usr/bin/env bash
set -euo pipefail

docker build -q -t ot-lab-modbus-server-test ./modbus/server >/dev/null

set +e
timeout 3 docker run --rm ot-lab-modbus-server-test \
  python /server.py >/tmp/ot-lab-modbus-server-test.log 2>&1
server_status=$?
set -e

if [ "$server_status" -ne 124 ]; then
  cat /tmp/ot-lab-modbus-server-test.log >&2
  exit 1
fi

if grep -Fq "deprecated" /tmp/ot-lab-modbus-server-test.log; then
  cat /tmp/ot-lab-modbus-server-test.log >&2
  exit 1
fi
