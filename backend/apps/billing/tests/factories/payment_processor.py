from factory.django import DjangoModelFactory


class PaymentProcessorFactory(DjangoModelFactory):
    name = 'Stripe'
    is_active = True

    class Meta:
        model = 'billing.PaymentProcessor'
        django_get_or_create = 'name',
