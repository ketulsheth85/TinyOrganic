from time import sleep

from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.utils import timezone
from sentry_sdk.utils import logger

from apps.core.tasks import HttpErrorRetryTask
from apps.orders.libs import OrderPaymentStatusEnum, OrderBuilder, CannotBuildOrderError
from celery_app import app
from libs import celery_helpers, locking
from libs.locking import FailedToAcquireSharedLockError
from libs.payment_processors.exceptions import CouldNotChargeOrderError, CouldNotProcessChargeError


@shared_task
def create_new_orders_for_active_subscribers():
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')
    today = timezone.now().date()

    errors = []
    for subscription in CustomerSubscription.objects.filter(
        is_active=True,
        next_order_charge_date=today,
        customer__payment_methods__is_valid=True,
        customer__addresses__isnull=False,
    ).distinct('customer_child'):
        try:
            order = OrderBuilder.from_subscription(subscription)
            print(f'Created order {order}')
        except CannotBuildOrderError as e:
            errors.append(e)
            # todo: send email with issue?
        finally:
            subscription.update_next_order_dates()
            subscription.save()
            subscription.customer_child.cart.remove_onetime_line_items()

    if errors:
        logger.error(errors)

    return 'Created new orders for active subscribers'


@shared_task(base=HttpErrorRetryTask, rate_limit='2/s')
def _charge_order(order_id: str):
    Order = apps.get_model('orders', 'Order')

    with locking.acquire_shared_lock_context(f'_charge-order-{order_id}', 'celery'):
        try:
            order = Order.objects.get(
                id=order_id,
                payment_status=str(OrderPaymentStatusEnum.pending),
                customer_child__subscription__is_active=True,
                payment_processor_charge_id__isnull=True,
            )
            order.charge_attempts += 1
            order.save()
            order.refresh_from_db()
            order.charge()
            order.save()
        except (
            CouldNotChargeOrderError,
            CouldNotProcessChargeError,
            Order.DoesNotExist,
            FailedToAcquireSharedLockError,
        ) as e:
            logger.error(e)
            return f'Could not charge order: {order_id}'

    return f'Charged order: {order}'


@shared_task
@celery_helpers.prevent_multiple
def charge_new_orders():
    Order = apps.get_model('orders', 'Order')

    uncharged_orders = Order.objects.filter(
        payment_status=str(OrderPaymentStatusEnum.pending),
        payment_processor_charge_id__isnull=True,
        customer_child__subscription__is_active=True,
    )[:40]

    for order in uncharged_orders:
        _charge_order(order.id)

    return f'Sent {uncharged_orders.count()} orders to be charged'


@shared_task(soft_time_limit=60*60*1000)
@celery_helpers.prevent_multiple
def sync_unsynced_orders_to_shopify():
    Order = apps.get_model('orders', 'Order')
    from apps.orders.tasks.order import sync_order_to_shopify
    unsynced_orders = Order.objects.filter(
        external_order_id__isnull=True,
        synced_to_shopify=False,
        shipping_rate__isnull=False,
        order_number__isnull=True,
        customer__addresses__isnull=False,
        payment_status=str(OrderPaymentStatusEnum.paid),
        payment_processor_charge_id__isnull=False,
    ).order_by(
        'customer__email',
    )[:15]

    errors = []
    for order in unsynced_orders:
        if not settings.TESTING:
            # todo: revisit whether these should be async
            sleep(4)
        try:
            sync_order_to_shopify(order.id)
            if not settings.TESTING:
                sleep(4)
        except Exception as e:
            errors.append(e)

    if errors:
        raise Exception(errors)

    return f'Synced all unsynced orders to shopify'


@shared_task(soft_time_limit=60*60*1000)
@celery_helpers.prevent_multiple
def sync_unsynced_orders_to_tax_client():
    from apps.orders.tasks.order import sync_order_to_tax_client
    Order = apps.get_model('orders', 'Order')
    unsynced_orders = Order.objects.filter(
        synced_to_avalara=False,
        payment_status=str(OrderPaymentStatusEnum.paid),
    )[:50]

    errors = []
    for order in unsynced_orders:
        try:
            sync_order_to_tax_client(order.id)
        except Exception as e:
            errors.append(e)

    if errors:
        raise Exception(errors)

    return f'Synced {unsynced_orders.count()} orders to tax client'


@app.task
def delete_pending_order(order_id: str):
    Order = apps.get_model('orders', 'Order')
    order = Order.objects.get(id=order_id)
    order.line_items.filter().delete()
    order.applied_discount = None
    order.delete()
    return f'Deleted {order_id}'


@app.task
def delete_pending_orders():
    Order = apps.get_model('orders', 'Order')

    pending_orders = Order.objects.filter(
        payment_status=str(OrderPaymentStatusEnum.pending),
        payment_method__isnull=True
    )

    for order in pending_orders:
        delete_pending_order.delay(order.id)

    return f'Deleted {pending_orders.count()} Orders'


@app.task
def delete_pending_orders_for_non_subscribers():
    Order = apps.get_model('orders', 'Order')

    non_subscriber_pending_orders = Order.objects.filter(
        payment_status=str(OrderPaymentStatusEnum.pending),
        customer_child__subscription__is_active=False,
    )

    for order in non_subscriber_pending_orders:
        delete_pending_order.delay(order.id)

    return f'Deleted {non_subscriber_pending_orders.count()} orders'
