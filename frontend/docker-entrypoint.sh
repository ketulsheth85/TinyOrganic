#!/usr/bin/env sh

set -e 

cd /app/frontend
npm install

if [ "$1" = 'run' ]; then
  if [ "$2" = 'dev' ]; then
    exec npm run dev
  fi
  if [ "$2" = 'test' ]; then
    exec npm run test
  fi
fi

if [ "$1" = 'build' ]; then
  exec npm build
fi

exec "$@"
