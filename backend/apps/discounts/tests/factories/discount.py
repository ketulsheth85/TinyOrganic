from decimal import Decimal

import factory
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyText

from apps.customers.tests.factories import CustomerChildFactory, CustomerFactory


class DiscountFactory(DjangoModelFactory):
    codename = FuzzyText(prefix='discount-')
    discount_type = FuzzyChoice(choices=('percentage', 'fixed amount'))
    amount = Decimal('20')

    class Meta:
        model = 'discounts.Discount'


class CustomerDiscountFactory(DjangoModelFactory):
    customer = SubFactory(CustomerFactory)
    discount = SubFactory(DiscountFactory)
    customer_child = SubFactory(CustomerChildFactory)

    class Meta:
        model = 'discounts.CustomerDiscount'
