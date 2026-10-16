#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
exec docker compose -p tapajos-platform -f docker/docker-compose.yml -f docker/compose.telemac.yml stop
