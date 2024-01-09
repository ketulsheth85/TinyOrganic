import shlex
import subprocess

import environ
from django.core.management.base import BaseCommand
from django.utils import autoreload

env = environ.Env()


# see: https://medium.com/aubergine-solutions/2ba8e313eb37
def restart_celery(*args, **kwargs):
    kill_worker_cmd = 'pkill -9 celery'
    subprocess.call(shlex.split(kill_worker_cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    start_worker_cmd = 'docker-entrypoint.sh worker-only'
    subprocess.call(shlex.split(start_worker_cmd))


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Starting celery worker with management command with autoreload...')
        autoreload.run_with_reloader(restart_celery, args=None, kwargs=None)
