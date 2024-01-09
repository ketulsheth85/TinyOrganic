import uuid

from django.test import TestCase

from apps.orders.tests.factories import OrderFactory
from apps.webhooks.tasks import process_updated_orders_from_webhook_events
from apps.webhooks.tests.factories import WebhookFactory, WebhookEventFactory


class WebhookEventTaskTestSuite(TestCase):
    def setUp(self) -> None:
        self.webhook = WebhookFactory(topic='orders/updated')

    def test_will_set_webhook_event_as_processed(self):
        WebhookEventFactory(webhook=self.webhook, data={})
        process_updated_orders_from_webhook_events()
        self.assertTrue(self.webhook.events.first().is_processed)

    def test_will_update_the_fulfillment_status_of_the_order(self):
        order = OrderFactory(external_order_id='some-order-id')
        WebhookEventFactory(
            webhook=self.webhook,
            data={
                'fulfillment_status': 'fulfilled',
                'fulfillments': [{'order_id': 'some-order-id', 'tracking_number': '12345'}]
            },
            external_id=str(uuid.uuid4()),
        )
        process_updated_orders_from_webhook_events()
        order.refresh_from_db()
        self.assertIsNotNone(order.tracking_number)
