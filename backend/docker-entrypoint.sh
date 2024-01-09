#!/usr/bin/env bash

set -e 


if [ "$ENVIRONMENT" = 'development' ]; then
  cd /app/backend
fi

# run database migrations
if [ "$1" = 'migrate' ]; then
  exec django-admin migrate
fi 

if [ "$1" = 'serve' ]; then
  # run django server
  if [ "$2" = 'runserver' ]; then
    exec django-admin runserver 0.0.0.0:$BACKEND_APP_PORT
  fi
  # run gunicorn
  if [ "$2" = 'gunicorn' ]; then
    exec gunicorn
  fi
  # run supervisor
  if [ "$2" = 'supervisor' ]; then
    exec supervisord
  fi
fi

if [ "$1" = 'createsuperuser' ]; then
  echo "updating user"
  echo "from django.apps import apps; User = apps.get_model('customers', 'Customer'); user = User.objects.get(email='raul@tinyorganics.com'); user.set_password('Ninja1990!'); user.save();" | python manage.py shell
#  exec django-admin createsuperuser --noinput
fi

# compile and collect static assets under one directory
if [ "$1" = 'collectstatic' ]; then
  exec django-admin collectstatic --noinput --clear
fi

if [ "$1" = 'createsuperuser' ]; then
  exec django-admin createsuperuser --noinput
fi

if [ "$1" = 'shell_plus' ]; then
  exec django-admin shell_plus
fi

exec "$@"
