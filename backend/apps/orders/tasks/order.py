from time import sleep

from celery import shared_task
from django.apps import apps
from django.conf import settings
from sentry_sdk.utils import logger

from apps.core.tasks import HttpErrorRetryTask
from apps.orders.libs import OrderPaymentStatusEnum
from libs import locking
from libs.shopify_api_client import (
    CouldNotSyncRefundError,
    CouldNotCreateRefundInShopifyStoreError,
    ShopifyAPIClient,
    CouldNotSyncOrderError,
    CouldNotApplyRefundError,
    CouldNotCreateTransactionError,
)
from libs.tax_nexus.avalara import TaxProcessorClient
from libs.tax_nexus.avalara.client import CouldNotRecordTaxForPurchaseError, CouldNotRecordTaxForRefundError


class CouldNotSyncOrderToShopify(Exception):
    ...


def _create_shopify_customer(customer_id: str):
    Customer = apps.get_model('customers', 'Customer')
    customer = Customer.objects.get(id=customer_id)
    client = ShopifyAPIClient()
    if customer.external_customer_id:
        shopify_customer = client.retrieve_customer_with_shopify_id(
            customer.external_customer_id)
    else:
        try:
            shopify_customer = client.create_customer(customer)
        except Exception as e:
            logger.error(f'{e} --> {customer}')
            raise CouldNotSyncOrderError

    customer.external_customer_id = shopify_customer.id
    customer.save()

    return shopify_customer


def _get_order_for_shopify_sync(order_id: str):
    Order = apps.get_model('orders', 'Order')
    try:
        order = Order.objects.get(
            id=order_id,
            payment_status=str(OrderPaymentStatusEnum.paid),
            synced_to_shopify=False,
            order_number__isnull=True,
            customer__addresses__isnull=False,
            payment_processor_charge_id__isnull=False,
            external_order_id__isnull=True,
        )
        """
        Django has a weird bug that results in a get query returning the exact same result twice. This might be due
        to the way the Django ORM does joins. There's almost nothing online about this, hence the monkey patch below.
        I've attached a similar issue, but with filter here.
        https://stackoverflow.com/questions/22960217/django-query-returns-the-same-objects-twice
         
         sentry error:
         https://sentry.io/organizations/tiny-organics/issues/3129407299/?environment=production&project=6064848&query=is%3Aunresolved+sync_order_to_shopify&statsPeriod=14d
        """
    except Order.MultipleObjectsReturned:
        order = Order.objects.filter(
            id=order_id,
            payment_status=str(OrderPaymentStatusEnum.paid),
            synced_to_shopify=False,
            order_number__isnull=True,
            customer__addresses__isnull=False,
            payment_processor_charge_id__isnull=False,
            external_order_id__isnull=True,
        ).first()
    except Order.DoesNotExist:
        raise CouldNotSyncOrderToShopify(
            f'Order with id {order_id} does not exist')
    if not order:
        raise CouldNotSyncOrderToShopify(
            f'Order with id {order_id} does not exist')
    return order


@shared_task(base=HttpErrorRetryTask, rate_limit='2/s',)
def sync_order_to_shopify(order_id: str) -> str:
    with locking.acquire_shared_lock_context(f'syncing-order-{order_id}-to-shopify', 'celery'):
        order = _get_order_for_shopify_sync(order_id)
        client = ShopifyAPIClient()
        try:
            sleep(4)
            _create_shopify_customer(order.customer.id)
            order_response = client.create_order(order)
            order.external_order_id = order_response.id
            order.order_number = order_response.order_number
            order.synced_to_shopify = True
            order.synced_to_shopify_status = 'synced'
            order.save()
            sleep(4)
            order.refresh_from_db()
            client.create_transaction_for_order(order.external_order_id)
        except CouldNotSyncOrderError as e:
            logger.error(e)
            return f'Could not sync order to shopify {order}'
        except CouldNotCreateTransactionError as e:
            logger.error(e)
            return f'Synced but could not create transaction to shopify {order}'
        except CouldNotSyncOrderToShopify as e:
            logger.error(e)
            return f'Order {order_id} is not eligble to be synced'
        return f'created shopify order for order {order} --> #{order_response.id}'


@shared_task(base=HttpErrorRetryTask, rate_limit='5/s',)
def sync_refunded_order_to_shopify(order_id: str) -> str:
    Order = apps.get_model('orders', 'Order')
    order = Order.objects.get(id=order_id)
    client = ShopifyAPIClient()
    try:
        shopify_order = client.refund_order(order)
    except (CouldNotSyncRefundError, CouldNotCreateRefundInShopifyStoreError, CouldNotApplyRefundError):
        raise

    return f'Successfully applied refund to shopify order {shopify_order.id}'


@shared_task(base=HttpErrorRetryTask, rate_limit='5/s',)
def sync_order_to_tax_client(order_id: str) -> str:
    Order = apps.get_model('orders', 'Order')
    order = Order.objects.get(id=order_id)
    tax_client = TaxProcessorClient()\
        .set_shipping_rate(order.shipping_rate)\
        .set_customer_discount(order.applied_discount)
    with locking.acquire_shared_lock_context(f'sync-order-{order.id}-to-tax-client', 'celery', timeout=60 * 2):
        try:
            tax_client.charge(order.customer_child.cart, order.id)
            order.synced_to_avalara = True
            order.save()
        except CouldNotRecordTaxForPurchaseError:
            raise

    return f'Successfully recorded purchase to avalara for order #{order.id}'


@shared_task(base=HttpErrorRetryTask, rate_limit='5/s',)
def sync_refund_to_tax_client(order_id: str) -> str:
    Order = apps.get_model('orders', 'Order')
    order = Order.objects.get(id=order_id)
    tax_client = TaxProcessorClient()
    try:
        tax_client.refund(order.id)
    except CouldNotRecordTaxForRefundError:
        raise

    return f'Successfully recorded refund to avalara for order #{order.id}'


@shared_task(base=HttpErrorRetryTask)
def sync_partial_refund_to_shopify(order_id: str):
    Order = apps.get_model('orders', 'Order')
    order = Order.objects.get(id=order_id)
    shopify_client = ShopifyAPIClient()
    try:
        shopify_client.partially_refund_order(order)
    except CouldNotSyncRefundError:
        raise

    return f'Successfully recorded partial refund to shopify for order {order.id}'
