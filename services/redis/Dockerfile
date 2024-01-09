# Ensure this version is consistent with the production Redis version (e.g. ElastiCache).
ARG REDIS_VERSION=5.0.6

FROM redis:${REDIS_VERSION}-alpine AS redis

COPY health-check.sh /usr/local/bin/

HEALTHCHECK --interval=5s --timeout=3s \
       CMD health-check.sh
