from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText


class WebhookFactory(DjangoModelFactory):
    name = FuzzyText(prefix='webhook-')
    topic = FuzzyText(prefix='orders/')
    endpoint_url = FuzzyText(prefix='https://tiny-domain.com/')

    class Meta:
        model = 'webhooks.Webhook'
