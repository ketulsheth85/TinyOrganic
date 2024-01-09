from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger

from apps.orders.tests.factories import OrderFactory
from apps.products.tests.factories import ProductFactory, ProductVariantFactory


class OrderLineItemFactory(DjangoModelFactory):
    order = SubFactory(OrderFactory)
    product = SubFactory(ProductFactory)
    quantity = FuzzyInteger(low=1, high=12)
    product_variant = SubFactory(ProductVariantFactory)

    class Meta:
        model = 'orders.OrderLineItem'
