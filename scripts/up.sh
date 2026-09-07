#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

startup_timeout=${STARTUP_TIMEOUT_SECONDS:-60}
if ! [[ "$startup_timeout" =~ ^[0-9]+$ ]]; then
  printf 'STARTUP_TIMEOUT_SECONDS must be a non-negative integer.\n' >&2
  exit 2
fi

if ! command -v docker >/dev/null 2>&1; then
  printf 'Docker is not installed or is not available on PATH.\n' >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  printf 'Docker is not running or cannot be accessed by this user.\n' >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  printf 'Docker Compose is not available. Install the Docker Compose plugin.\n' >&2
  exit 1
fi

if ! docker network inspect ot-net >/dev/null 2>&1; then
  printf 'Creating Docker network ot-net (10.20.0.0/24)...\n'
  docker network create \
    --driver bridge \
    --subnet 10.20.0.0/24 \
    ot-net >/dev/null
fi

printf 'Starting the OT lab stack...\n'
if ! docker compose up -d --build; then
  printf '\nFailed to start the Compose stack. Current status:\n' >&2
  docker compose ps >&2 || true
  printf '\nRecent logs:\n' >&2
  docker compose logs --tail 50 >&2 || true
  exit 1
fi

mapfile -t expected_services < <(docker compose config --services)
expected_count=${#expected_services[@]}
if [ "$expected_count" -eq 0 ]; then
  printf 'No services are declared in the Compose configuration.\n' >&2
  exit 1
fi

expected=$(printf '%s\n' "${expected_services[@]}" | sort)
deadline=$((SECONDS + startup_timeout))

while true; do
  running=$(docker compose ps --status running --services | sort)
  if [ "$running" = "$expected" ]; then
    printf '\n'
    docker compose ps
    printf '\nAll %d services are running.\n' "$expected_count"
    exit 0
  fi

  if (( SECONDS >= deadline )); then
    break
  fi

  sleep 2
done

printf '\nTimed out waiting for all %d services after %d seconds.\n' \
  "$expected_count" "$startup_timeout" >&2
printf '\nCurrent status:\n' >&2
docker compose ps >&2 || true
printf '\nRecent logs:\n' >&2
docker compose logs --tail 50 >&2 || true
exit 1
