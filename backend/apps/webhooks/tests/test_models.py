from unittest import mock

from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response

from apps.webhooks.tests.factories import WebhookFactory


def _mock_webhook_subscription_request(*args, **kwargs):
    return Response({}, status=status.HTTP_201_CREATED)


class WebhookTestSuite(TestCase):
    def test_will_attempt_to_subscribe_to_receive_webhook_event(self):
        with self.captureOnCommitCallbacks(execute=True):
            with mock.patch(
                'apps.webhooks.models.webhook.Webhook._subscribe_to_webhook_topic',
                side_effect=lambda *args: True,
            ) as mocked:
                webhook = WebhookFactory()
                webhook.is_active = True
                webhook.save()
        self.assertTrue(mocked.called)
