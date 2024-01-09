import datetime
import inspect

from contextlib import contextmanager

from django.core.cache import caches

from hashlib import sha1

from libs.test_helpers import inside_test


def _get_cache(cache_name):
    return caches[cache_name]


# Given a function and its arguments, generates a unique string that can be reliably used to distinguish
# calls to thus function with specific arguments.
def func_unique_key(func, args, kwargs):
    function = '{module}.{function}'.format(module=inspect.getmodule(func).__name__,
                                            function=func.__name__)
    arguments = inspect.signature(func).bind(*args, **kwargs).arguments
    argument_as_string = str(','.join(['{k}={v}'.format(k=k, v=v) for k, v in arguments.items()]))
    hashed_arguments = sha1(argument_as_string.encode('utf-8')).hexdigest()
    return '{function}-{hashed_arguments}'.format(function=function, hashed_arguments=hashed_arguments)


class FailedToAcquireSharedLockError(Exception):
    pass


def acquire_shared_lock(lock_name, cache_name='default', timeout=24*60*60):
    cache = _get_cache(cache_name)
    key = 'lock-{}'.format(lock_name)
    value = datetime.datetime.now()
    if cache.add(key, value, timeout) or inside_test():
        return key
    else:
        raise FailedToAcquireSharedLockError(lock_name)


def release_shared_lock(lock_key, cache_name='default'):
    return bool(_get_cache(cache_name).delete(lock_key)) or inside_test()


@contextmanager
def acquire_shared_lock_context(lock_name, cache_name='default', timeout=3*60*60):
    lock_key = None
    try:
        lock_key = acquire_shared_lock(lock_name, cache_name, timeout)
        yield lock_key
    finally:
        if lock_key:
            release_shared_lock(lock_key, cache_name)
