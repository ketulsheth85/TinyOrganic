from decimal import Decimal

from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText


class ShippingRateFactory(DjangoModelFactory):
    title = FuzzyText(prefix='flat-')
    price = Decimal('5.99')
    is_active = True

    class Meta:
        model = 'orders.ShippingRate'
