from decimal import Decimal

from celery import shared_task
from django.apps import apps
from django.utils import timezone

from apps.core.exceptions import APIRateLimitError
from apps.core.tasks import ReChargeErrorRetryTask
from libs.recharge_rest_client import RechargeClient
from libs.shopify_rest_client import ShopifyRestClient


@shared_task(base=ReChargeErrorRetryTask, rate_limit='2/s')
def log_queued_orders_for_customer(customer_id: str):
    client = RechargeClient()
    Customer = apps.get_model('customers', 'Customer')

    customer = Customer.objects.get(id=customer_id)
    request = client.get_queued_orders(
        recharge_customer_id=customer.external_customer_id,
        customer_id=customer_id,
    )
    if request.response.status_code == 429:
        raise APIRateLimitError

    return f'Logged Queued Orders for {customer}'


@shared_task(base=ReChargeErrorRetryTask, rate_limit='2/s')
def cancel_recharge_subscription(subscription_id: str, recharge_subscription_id: str, comment: str):
    client = RechargeClient()

    request = client.cancel_subscription_with_recharge_subscription_id(
        recharge_subscription_id,
    )
    if request.response.status_code == 429:
        raise APIRateLimitError

    return f'Cancelled Subscription {subscription_id} in ReCharge'


@shared_task(base=ReChargeErrorRetryTask, rate_limit='2/s')
def _cancel_queued_order(recharge_order_id: str, customer_id: str):
    client = RechargeClient()
    Customer = apps.get_model('customers', 'Customer')
    customer = Customer.objects.get(id=customer_id)

    request = client.delete_queued_order(
        recharge_order_id,
    )
    if request.response.status_code == 429:
        raise APIRateLimitError

    return f'Deleted queued order for {customer}'


@shared_task(base=ReChargeErrorRetryTask, rate_limit='2/s')
def cancel_recharge_queued_orders(customer_id: str):
    Customer = apps.get_model('customers', 'Customer')
    APIRequestLog = apps.get_model('core', 'APIRequestLog')

    customer = Customer.objects.get(id=customer_id)

    request_log = APIRequestLog.objects.get(
        response_status_code=200,
        object_type='CustomerOrder',
        object_id=customer_id,
        request_url__icontains=f'https://api.rechargeapps.com/orders/'
                               f'?external_customer_id={customer.external_customer_id}',
    )
    for recharge_queued_order in request_log.response_json_payload.get('orders', []):
        _cancel_queued_order.delay(recharge_queued_order['id'], customer_id)

    return f'Cancelling orders for {customer}'
