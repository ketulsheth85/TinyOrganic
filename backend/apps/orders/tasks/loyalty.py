from celery import shared_task
from django.apps import apps
from sentry_sdk.utils import logger
from typing import List, Optional
from decimal import Decimal

from apps.core.tasks import HttpErrorRetryTask
from libs import locking
from libs.yotpo_client import (
    YotpoClient,
    CouldNotCreateYotpoOrderError,
    CouldNotCreateYotpoRefundError,
    LoyaltyProgramItem,
    LoyaltyProgramOrder,
    LoyaltyProgramRefund,
)
from apps.orders.libs import OrderPaymentStatusEnum
from apps.discounts.libs import CustomerDiscountStatusEnum

class CouldNotSyncOrderToYotpo(Exception):
    ...


class CouldNotSyncRefundToYotpo(Exception):
    ...


def _get_order_for_yotpo_sync(order_id: str):
    Order = apps.get_model('orders', 'Order')
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise CouldNotSyncOrderToYotpo(
            f'Order with id {order_id} does not exist')
    return order


def _dollar_amount_to_cents(amount: Decimal) -> int:
    return int(amount * Decimal('100'))


def _item_to_dict(item) -> dict:
    return LoyaltyProgramItem(
                name=item.product.title,
                price_cents=_dollar_amount_to_cents(item.product_variant.price),
                vendor='Tiny Organics inc',
                id=item.product.external_product_id,
                type=item.product.product_type,
                quantity=item.quantity,
                collections=', '.join(map(str, item.product.tags)),
            ).to_dict()


def _line_items_to_list(line_items) -> List[dict]:
    return [_item_to_dict(item) for item in line_items]


def _get_coupon_code(coupon) -> Optional[str]:
    coupon_code = None
    if coupon and coupon.status is CustomerDiscountStatusEnum.redeemed:
        coupon_code = coupon.discount.codename

    return coupon_code


def _create_yotpo_loyalty_order(order) -> LoyaltyProgramOrder:
    loyalty_order = LoyaltyProgramOrder(
        customer_email=order.customer.email,
        total_amount_cents=_dollar_amount_to_cents(order.amount_total),
        currency_code='USD',
        order_id=str(order.id),
        status='paid',
        coupon_code=_get_coupon_code(order.applied_discount),
        ignore_ip_ua=True,
        discount_amount_cents=_dollar_amount_to_cents(order.discount_amount_total),
        items=_line_items_to_list(order.line_items.filter())
    )

    return loyalty_order


@shared_task(base=HttpErrorRetryTask, rate_limit='2/s',)
def sync_order_to_yotpo(order_id: str):
    with locking.acquire_shared_lock_context(f'syncing-order-{order_id}-to-yotpo', 'celery'):
        """
        The loyalty_order is hard coded to 'paid' in _create_yotpo_loyalty_order() since
        this task to sync the order to yotpo would not kick off unless the order was paid.
        """
        order = _get_order_for_yotpo_sync(order_id)
        if not order.synced_to_yotpo:
            loyalty_order = _create_yotpo_loyalty_order(order)
            client = YotpoClient()
            try:
                client.create_order(loyalty_order)
                order.synced_to_yotpo = True
                order.save()
            except CouldNotCreateYotpoOrderError as e:
                logger.error(e)
                return f'Could not sync order to yotpo {loyalty_order}'
            except CouldNotSyncOrderToYotpo as e:
                logger.error(e)
                return f'Order {order_id} is not eligible to be synced'
            return f'created yotpo order for order #{order_id}'


def _get_refund_amount_in_cents(order) -> int:
    if order.payment_status is OrderPaymentStatusEnum.refunded:
        return _dollar_amount_to_cents(order.amount_total)
    elif order.payment_status is OrderPaymentStatusEnum.partially_refunded:
        return _dollar_amount_to_cents(order.partial_refund_amount)


@shared_task(base=HttpErrorRetryTask, rate_limit='2/s',)
def sync_refund_to_yotpo(order_id: str):
    with locking.acquire_shared_lock_context(f'syncing-refund-for-order-#{order_id}-to-yotpo', 'celery'):
        order = _get_order_for_yotpo_sync(order_id)
        if order.synced_to_yotpo:
            loyalty_refund = LoyaltyProgramRefund(
                order_id=str(order.id),
                total_amount_cents=_get_refund_amount_in_cents(order),
                currency='USD',
            )
            client = YotpoClient()
            try:
                client.create_refund(loyalty_refund)
            except CouldNotCreateYotpoRefundError as e:
                logger.error(e)
                return f'Could not sync refund to yotpo {loyalty_refund}'
            except CouldNotSyncRefundToYotpo as e:
                logger.error(e)
                return f'Refund for order #{order_id} is not eligible to be synced'
            return f'created yotpo refund for order #{order_id}'
