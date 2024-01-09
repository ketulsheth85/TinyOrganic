from django.utils import timezone
from factory import SubFactory, lazy_attribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDecimal, FuzzyText

from apps.billing.tests.factories import PaymentProcessorFactory
from apps.customers.tests.factories import CustomerFactory


class PaymentMethodFactory(DjangoModelFactory):
    customer = SubFactory(CustomerFactory)
    payment_processor = SubFactory(PaymentProcessorFactory)
    payment_processor_payment_method_id = FuzzyText(prefix='pm_')
    last_four = FuzzyDecimal(1000, 1100)

    @lazy_attribute
    def expiration_date(self):
        return timezone.now().date()

    class Meta:
        model = 'billing.PaymentMethod'
