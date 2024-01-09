#!/usr/bin/env bash

NEW_RELIC_CONFIG_FILE=/app/config/newrelic.ini
export NEW_RELIC_CONFIG_FILE

newrelic-admin run-program gunicorn --config ./config/gunicorn.py --access-logfile=- --error-logfile=- wsgi:application
