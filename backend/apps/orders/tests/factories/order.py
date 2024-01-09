from decimal import Decimal
from backend.apps.discounts.tests.factories.discount import CustomerDiscountFactory

from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from apps.billing.tests.factories import PaymentMethodFactory
from apps.customers.tests.factories import CustomerFactory, CustomerChildFactory
from apps.orders.tests.factories import ShippingRateFactory


class OrderFactory(DjangoModelFactory):
    customer = SubFactory(CustomerFactory)
    customer_child = SubFactory(CustomerChildFactory)
    amount_total = Decimal('10')
    tax_total = Decimal('2')
    external_order_id = FuzzyText(prefix='shopify_id-')
    shipping_rate = SubFactory(ShippingRateFactory)
    payment_method = SubFactory(PaymentMethodFactory)
    applied_discount = SubFactory(CustomerDiscountFactory)

    class Meta:
        model = 'orders.Order'
