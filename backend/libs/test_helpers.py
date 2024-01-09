import random

from functools import wraps

from django.conf import settings
from django.test import TestCase, override_settings


def make_id_generator():
    ids = {}
    def get_id(max=100000):
        id = random.randint(1, max)
        if id in ids:
            id = get_id(max)
        return id
    return get_id


get_random_id = make_id_generator()


class BaseTestCase(TestCase):
    @override_settings(TESTING=True)
    def run(self, result=None):
        super().run(result)


def inside_test():
    return settings.TESTING


def skip_during_testing(func):
    @wraps(func)
    def skip(*args, **kwargs):
        if inside_test():
            return
        else:
            return func(*args, **kwargs)
    return skip
