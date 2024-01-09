# Decorator to prevent the concurrent execution of multiple instances of the same task. It must be the 'inner-most'
# decorator on a function.
from functools import wraps

from libs.locking import func_unique_key, acquire_shared_lock_context


def prevent_multiple(task):
    @wraps(task)
    def wrapper(*args, **kwargs):
        lock_name = func_unique_key(task, args, kwargs)
        # Make sure we use the celery broker as our cache since it is the only cache
        # that is shared and not local.
        cache_name = 'celery'
        # todo: change lock name to git revision number
        with acquire_shared_lock_context(f'locking-{lock_name}', cache_name) as _:
            return task(*args, **kwargs)
    return wrapper
