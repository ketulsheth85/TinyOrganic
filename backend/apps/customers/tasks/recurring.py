from datetime import timedelta
from time import sleep

import analytics
from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from apps.core.exceptions import APIRateLimitError
from apps.core.tasks import HttpErrorRetryTask
from libs import celery_helpers
from libs.email import _scrub_email_address
from apps.customers.tasks.notification import (
    sync_subscription_activated_event,
    sync_subscription_cancelled_event,
    sync_klaviyo_profile_fields_event,
)


@shared_task
def _send_email(
    subject: str,
    text_body: str,
    html_body: str,
    email_address: str,
):
    msg = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        to=[_scrub_email_address(email_address), ],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()


@shared_task(base=HttpErrorRetryTask, soft_time_limit=60 * 60 * 1000)
def send_upcoming_charge_notification_to_active_subscribers():
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')

    active_subscriptions_with_upcoming_charges = CustomerSubscription.objects.filter(
        is_active=True,
        next_order_charge_date=timezone.now() + timedelta(days=3),
    ).order_by('customer__email')

    for subscription in active_subscriptions_with_upcoming_charges:
        subject = f'Make changes to your upcoming Tiny Organics shipment! ' \
                  f'Your order will process on {subscription.next_order_charge_date}'
        context = {'first_name': subscription.customer.first_name}
        html_body = render_to_string(
            'emails/customer_subscription/upcoming-charge.html', context)
        text_body = ''

        _send_email.delay(
            subject,
            text_body,
            html_body,
            subscription.customer.email,
        )

        if not settings.DEBUG and not settings.IS_TESTING:
            analytics.track(
                str(subscription.customer.id),
                'TO_OrderUpcoming',
                properties={
                    'active_subscription': True,
                    'first_name': subscription.customer.first_name,
                    'last_name': subscription.customer.last_name,
                    'email': subscription.customer.email,
                    'expected_order_date': str(subscription.next_order_charge_date),
                    'child_name': subscription.customer_child.first_name,
                    'child_birthdate': subscription.customer_child.birth_date,
                    'child_gender': subscription.customer_child.sex,
                }
            )
    analytics.flush()

    return 'Completed triggering upcoming order notification to active subscribers'


def _get_subscriptions(client, customer):
    APIRequestLog = apps.get_model('core', 'APIRequestLog')
    created = True
    subscription_log = APIRequestLog.objects.filter(
        object_type='ReChargeCustomerSubscription',
        object_id=customer.recharge_customer_id,
        response_status_code=200,
    ).first()
    if subscription_log:
        created = False
        subscriptions = subscription_log.response_json_payload['subscriptions']
    else:
        subscriptions_request = client.get_subscriptions_with_recharge_customer_id(
            recharge_customer_id=customer.recharge_customer_id,
            customer_id=customer.recharge_customer_id,
        )
        if subscriptions_request.response.status_code == 429:
            raise APIRateLimitError

        subscriptions = subscriptions_request.response.parsed_body['subscriptions']
    return subscriptions, created


def _cancel_subscription_request(client, recharge_subscription_id):
    response = client.cancel_subscription_with_recharge_subscription_id(
        recharge_subscription_id=recharge_subscription_id,
    )
    if response.status_code == 429:
        raise APIRateLimitError
    sleep(1)

    return response.json()


def _get_queued_orders(client, customer):
    APIRequestLog = apps.get_model('core', 'APIRequestLog')

    request_log = APIRequestLog.objects.filter(
        object_type='ReChargeCustomerQueuedOrder',
        object_id=customer.recharge_customer_id,
        response_status_code=200,
    ).first()
    created = False
    if request_log:
        queued_orders = request_log.response_json_payload['orders']
    else:
        request = client.get_queued_orders(
            recharge_customer_id=customer.recharge_customer_id,
            customer_id=customer.recharge_customer_id
        )
        if request.response.status_code == 429:
            raise APIRateLimitError
        created = True
        queued_orders = request.response.parsed_body['orders']
    return queued_orders, created


def _delete_queued_order_request(client, recharge_order_id):
    response = client.delete_queued_order(
        recharge_order_id=recharge_order_id,
    )
    if response.status_code == 429:
        raise APIRateLimitError
    sleep(2)
    return response.json()


@celery_helpers.prevent_multiple
@shared_task(base=HttpErrorRetryTask, soft_time_limit=60 * 60 * 1000)
def sync_active_subscriptions_to_segment():
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')
    errors = []
    active_subscriptions_that_have_not_been_synced_to_klaviyo = CustomerSubscription.objects.filter(
        is_active=True,
        synced_to_klaviyo=False,
    ).order_by('-activated_at')[:50]
    for subscription in active_subscriptions_that_have_not_been_synced_to_klaviyo:
        try:
            sync_subscription_activated_event(subscription.id)
        except Exception as e:
            errors.append(e)

    if errors:
        raise Exception(errors)

    return 'Sent synced subscription status to segment'


@celery_helpers.prevent_multiple
@shared_task(base=HttpErrorRetryTask, soft_time_limit=60 * 60 * 1000)
def sync_inactive_subscriptions_to_segment():
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')
    errors = []

    inactive_subscriptions_that_have_not_been_synced_to_klaviyo = CustomerSubscription.objects.filter(
        is_active=False,
        synced_to_klaviyo=False,
    ).order_by('-deactivated_at')[:50]
    for subscription in inactive_subscriptions_that_have_not_been_synced_to_klaviyo:
        try:
            sync_subscription_cancelled_event(subscription.id)
        except Exception as e:
            errors.append(e)

    if errors:
        raise Exception(errors)

    return 'Sent synced subscription status to segment'


@celery_helpers.prevent_multiple
@shared_task(base=HttpErrorRetryTask, soft_time_limit=60 * 60 * 1000)
def update_active_subscriber_profiles_to_segment():
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')
    errors = []
    active_subscriptions_whose_profile_have_not_been_updated_in_klaviyo = CustomerSubscription.objects.filter(
        is_active=True,
        updated_profile_fields_to_klaviyo=False,
    ).order_by('-activated_at')[:50]
    for subscription in active_subscriptions_whose_profile_have_not_been_updated_in_klaviyo:
        try:
            sync_klaviyo_profile_fields_event(subscription.id)
        except Exception as e:
            errors.append(e)

    if errors:
        raise Exception(errors)

    return 'Sent klaviyo profile field updates to segment'


@celery_helpers.prevent_multiple
@shared_task(base=HttpErrorRetryTask, soft_time_limit=60 * 60 * 1000)
def update_cancelled_subscriber_profiles_to_segment():
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')
    errors = []
    cancelled_subscriptions_whose_profile_have_not_been_updated_in_klaviyo = CustomerSubscription.objects.filter(
        is_active=False,
        updated_profile_fields_to_klaviyo=False,
    ).order_by('-activated_at')[:50]
    for subscription in cancelled_subscriptions_whose_profile_have_not_been_updated_in_klaviyo:
        try:
            sync_klaviyo_profile_fields_event(subscription.id)
        except Exception as e:
            errors.append(e)

    if errors:
        raise Exception(errors)

    return 'Sent Klaviyo profile field updates to segment'
