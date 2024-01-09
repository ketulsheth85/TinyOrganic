from __future__ import absolute_import, unicode_literals

import os

import environ
from celery.schedules import crontab

env = environ.Env()

from celery import Celery, shared_task  # noqa

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', env('DJANGO_SETTINGS_MODULE'))

app = Celery(
    env('CELERY_APP_NAME', default='celery_app'),
    backend=env('CELERY_RESULT_BACKEND_URL', default='redis://'),
    broker=env('CELERY_BROKER_URL', default='amqp://'),
)

# Ensure this is the canonical app across all threads.
# http://docs.celeryproject.org/en/latest/reference/celery.html#celery.Celery.set_default
app.set_default()

app.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': env.str('CELERY_RESULT_BACKEND_URL', default='redis://'),
        'default_timeout': 60
    }
}

app.conf.beat_schedule = {
    'create-subscription-orders': {
        'task': 'apps.orders.tasks.recurring.create_new_orders_for_active_subscribers',
        'schedule': crontab(hour=0, minute=1),
    },
    # 'charge-new-subscription-orders': {
    #   'task': 'apps.orders.tasks.recurring.charge_new_orders',
    #   'schedule': crontab(minute="*/10"),
    # },
    'create_yotpo_referral_discount_for_customers_without_referral_discount': {
        'task': 'apps.discounts.tasks.create_yotpo_referral_discount_for_customers_without_referral_discount',
        'schedule': crontab(minute="*/10"),
    },
    'create_yotpo_referral_discount_for_customers_with_non_yotpo_referral_discount': {
        'task': 'apps.discounts.tasks.create_yotpo_referral_discount_for_customers_with_non_yotpo_referral_discount',
        'schedule': crontab(minute="*/10")
    },
    'deactivate-queued-products': {
        'task': 'apps.products.tasks.deactivate_products_set_to_deactivate_today',
        'schedule': crontab(hour=0, minute=1),
    },
    'activate-queued-products': {
        'task': 'apps.products.tasks.activate_products_set_to_activate_today',
        'schedule': crontab(hour=0, minute=0),
    },
    # 'activate-queued-discount-codes': {
    #   'task': 'apps.discounts.tasks.activate_inactive_discount_codes',
    #   'schedule': crontab(hour=0, minute=0),
    # },
    'deactivate-expiring-discount-codes': {
        'task': 'apps.discounts.tasks.deactivate_expired_discount_codes',
        'schedule': crontab(hour=0, minute=0),
    },
    'process-updated-orders-from-webhook-events': {
        'task': 'apps.webhooks.tasks.process_updated_orders_from_webhook_events',
        'schedule': crontab(hour='*', minute=0),
    },
    'notify-active-subscribers-of-upcoming-order': {
        'task': 'apps.customers.tasks.recurring.send_upcoming_charge_notification_to_active_subscribers',
        'schedule': crontab(hour=6, minute=0),
    },
    'sync-unsynced-orders-to-shopify': {
        'task': 'apps.orders.tasks.recurring.sync_unsynced_orders_to_shopify',
        'schedule': crontab(minute='*/5'),
    },
    'sync-unsynced-orders-to-tax-client': {
        'task': 'apps.orders.tasks.recurring.sync_unsynced_orders_to_tax_client',
        'schedule': crontab(minute='*/12'),
    },
    'delete-pending-orders-for-non-subscribers': {
        'task': 'apps.orders.tasks.recurring.delete_pending_orders_for_non_subscribers',
        'schedule': crontab(minute='*/15'),
    },
    'sync-activated-subscriptions-to-segment': {
        'task': 'apps.customers.tasks.recurring.sync_active_subscriptions_to_segment',
        'schedule': crontab(minute='*/8'),
    },
    'sync-deactivated-subscriptions-to-segment': {
        'task': 'apps.customers.tasks.recurring.sync_inactive_subscriptions_to_segment',
        'schedule': crontab(hour='*/5'),
    },
    'update-active-subscriber-profiles-in-klaviyo': {
        'task': 'apps.customers.tasks.recurring.update_active_subscriber_profiles_to_segment',
        'schedule': crontab(minute='*/7'),
    },
    'update-cancelled-subscriber-profiles-in-klaviyo': {
        'task': 'apps.customers.tasks.recurring.update_cancelled_subscriber_profiles_to_segment',
        'schedule': crontab(minute='*/6'),
    },
}

app.conf.task_routes = {
    'apps.customers.tasks.imports.*': {'queue': 'data-import'},
    'apps.customers.tasks.recurring.*': {'queue': 'recurring'},
    'apps.customers.tasks.notifications.*': {'queue': 'notifications'},
    'apps.orders.tasks.recurring.*': {'queue': 'recurring'},
    'apps.orders.tasks.notifications.*': {'queue': 'notifications'},
    'apps.orders.tasks.imports.*': {'queue': 'data-import'},
    'apps.orders.tasks.order.*': {'queue': 'orders'},
    'apps.webhooks.tasks.*': {'queue': 'webhooks'},
}

app.conf.timezone = 'America/New_York'
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
