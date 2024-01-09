from .minimal import *

if COLLECTSTATIC:
    STATICFILES_DIRS = (
        REAL_STATIC_ROOT,
        join_to_base_dir('apps/core/static'),
    )
else:
    STATIC_ROOT = REAL_STATIC_ROOT
    STATICFILES_DIRS = (
        # REAL_STATIC_ROOT,
        join_to_base_dir('apps/core/static'),
    )

DEBUG = False
