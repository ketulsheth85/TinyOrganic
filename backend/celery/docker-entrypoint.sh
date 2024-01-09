#!/usr/bin/env bash

set -e


celery_worker() {
    NEW_RELIC_CONFIG_FILE=$PWD/config/newrelic.ini newrelic-admin run-program celery -A celery_app worker --loglevel=INFO --autoscale=10,1 -E -Ofair -Q celery,data-import,notifications,recurring,customers,orders,webhooks --pidfile=
}

celery_worker_dev() {
  celery -A celery_app worker --loglevel=INFO --autoscale=10,1 -E -Ofair -Q celery,data-import,notifications,recurring,customers,orders,webhooks --pidfile=
}

celery_flower() {
  celery -A celery_app flower --address=0.0.0.0 --port=5566 --loglevel=INFO
}

if [ "$1" = 'worker-only' ]; then
    celery_worker
fi

if [ "$1" = 'worker' ]; then
    if [ "$ENVIRONMENT" = 'development' ]; then
        cd /app/backend
        exec django-admin celery
        celery_worker_dev
    else
      celery_worker
    fi
fi

if [ "$1" = 'beat' ]; then
  if [ "$ENVIRONMENT" = 'development' ]; then
    cd /app/backend
  fi
  celery -A celery_app beat --pidfile=
fi

if [ "$1" = 'flower' ]; then
  celery_flower
fi

exec "$@"
