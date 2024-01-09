# Inspired from https://stackoverflow.com/questions/56748782/flask-application-scaling-on-kubernetes-and-gunicorn
# we will use kubernetes to scale horizontally.

import multiprocessing

import environ

env = environ.Env()

backlog = 2048
capture_output = True
keepalive = 5
max_requests = 2000
proc_name = 'backend'
reload = False
if env('ENVIRONMENT', default='development') == 'development':
    reload = True
bind = '0.0.0.0:8000'
workers = (2 * multiprocessing.cpu_count()) + 1
threads = 2 * multiprocessing.cpu_count()
worker_connections = 1
sendfile = True
timeout = 60
worker_class = 'gthread'
