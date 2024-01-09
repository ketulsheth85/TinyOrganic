from decimal import Decimal

from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from apps.billing.tests.factories import PaymentMethodFactory
from apps.customers.tests.factories import CustomerFactory


class ChargeFactory(DjangoModelFactory):
    customer = SubFactory(CustomerFactory)
    payment_method = SubFactory(PaymentMethodFactory)
    amount = Decimal('10')
    payment_processor_charge_id = FuzzyText(prefix='pi_')

    class Meta:
        model = 'billing.Charge'
