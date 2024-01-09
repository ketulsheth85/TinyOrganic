#!/usr/bin/env sh

# Add health check; Inspired by: https://github.com/docker-library/healthcheck/tree/master/postgres
# 127.0.0.1 is used to force postgres to not use the local unix socket
pg_isready --quiet --dbname $POSTGRES_DB --host 127.0.0.1 --username $POSTGRES_USER
