FROM node:14-bullseye-slim as core

WORKDIR /app/frontend

RUN apt-get update && apt-get install -y gcc && \
    npm install -g webpack webpack-cli webpack-dev-server

COPY docker-entrypoint.sh /usr/local/bin

FROM core as development
COPY . /app/frontend

RUN npm install

ENTRYPOINT ["docker-entrypoint.sh"]
EXPOSE 3000

FROM core as production
ENV NODE_ENV=production
COPY . /app/frontend

RUN npm install && npm build

ENTRYPOINT ["docker-entrypoint.sh"]
