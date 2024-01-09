import json

import requests
from celery import shared_task
from django.apps import apps
from django.conf import settings

from celery_app import app


@app.task
def subscribe_to_webhook_events(webhook_id: str):
    Webhook = apps.get_model('webhooks', 'Webhook')
    webhook = Webhook.objects.get(id=webhook_id)
    request_headers = {'Content-Type': 'application/json', 'X-Shopify-Access-Token': settings.SHOPIFY_PASSWORD}
    request_data = {'webhook': {'topic': webhook.topic, 'address': webhook.endpoint_url, 'format': webhook.format}}
    response = requests.post(
        f'https://{settings.SHOPIFY_DOMAIN}/admin/api/2021-10/webhooks.json',
        data=json.dumps(request_data),
        headers=request_headers,
    )
    if response.status_code == 201:
        webhook.is_active = True
        webhook.save()

    return response.json()


@shared_task
def process_updated_orders_from_webhook_events():
    Webhook = apps.get_model('webhooks', 'Webhook')
    webhook = Webhook.objects.get(topic='orders/updated')

    Order = apps.get_model('orders', 'Order')

    for event in webhook.events.filter(is_processed=False).distinct('external_id'):
        if event.data.get('fulfillment_status') in {'fulfilled', 'partially_fulfilled'}:
            fulfillment = event.data['fulfillments'][0]
            try:
                order = Order.objects.get(external_order_id=fulfillment['order_id'])
                order.tracking_number = fulfillment['tracking_number']
                order.fulfillment_status = event.data.get('fulfillment_status')
                order.save()
            except Order.DoesNotExist:
                ...
        event.is_processed = True
        event.save()
