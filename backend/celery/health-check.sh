#!/usr/bin/env bash

set -e
# Use non-localhost name to exercise network connectivity.
host="$(hostname -i || echo 'rabbitmq')"

rabbitmq-diagnostics -q ping
