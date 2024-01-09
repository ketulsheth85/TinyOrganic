from __future__ import absolute_import, unicode_literals

import logging
from http.client import RemoteDisconnected

import stripe

from celery_once import QueueOnce
from requests import HTTPError, exceptions

from apps.core.exceptions import APIRateLimitError

logger = logging.getLogger(__name__)


class HttpErrorRetryTask(QueueOnce):
    once = {
        'graceful': True,
        'unlock_before_run': False
    }
    retry_backoff = True
    autoretry_for = (HTTPError, exceptions.ConnectionError, RemoteDisconnected, )
    retry_kwargs = {'max_retries': 10}

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        kwargs = {}
        if logger.isEnabledFor(logging.DEBUG):
            kwargs['exc_info'] = exc
        logger.error(f'Task {task_id} failed to execute with details: {einfo} - {exc}', **kwargs)
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f'Task {task_id} succeeded with result: {retval}. args: {args} . kwargs: {kwargs}')
        super().on_success(retval, task_id, args, kwargs)


class StripeErrorRetryTask(HttpErrorRetryTask):
    autoretry_for = (
        HTTPError,
        exceptions.ConnectionError,
        RemoteDisconnected,
        stripe.error.StripeError,
        stripe.error.APIConnectionError,
    )
