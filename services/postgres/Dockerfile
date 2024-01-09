ARG POSTGRES_VERSION=12

FROM postgres:${POSTGRES_VERSION}-alpine AS postgres

COPY psqlrc /root/.psqlrc

COPY docker-entrypoint-initdb.d/* /docker-entrypoint-initdb.d/

COPY health-check.sh /usr/local/bin

HEALTHCHECK --interval=5s --timeout=3s CMD ["health-check.sh"]
