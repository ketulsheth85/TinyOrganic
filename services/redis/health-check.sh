#!/usr/bin/env sh

# Ported from: https://github.com/docker-library/healthcheck/blob/master/redis/docker-healthcheck
set -eo

# Use non-localhost name to exercise network connectivity.
host="$(hostname -i || echo '127.0.0.1')"

if ping="$(redis-cli -h "$host" ping)" && [ "$ping" = 'PONG' ]; then
	exit 0
fi

exit 1
