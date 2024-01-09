from factory import SubFactory
from factory.django import DjangoModelFactory

from apps.webhooks.tests.factories import WebhookFactory


class WebhookEventFactory(DjangoModelFactory):
    webhook = SubFactory(WebhookFactory)

    class Meta:
        model = 'webhooks.WebhookEvent'
