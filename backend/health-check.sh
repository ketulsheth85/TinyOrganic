#!/usr/bin/env sh

wget --quiet --tries=1 --spider --header="Accept: application/json" \
    http://localhost:$BACKEND_APP_PORT/health-check/ || exit 1
