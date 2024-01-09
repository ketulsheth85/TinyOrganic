from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger

from apps.carts.tests.factories import CartFactory
from apps.products.tests.factories import ProductFactory, ProductVariantFactory


class CartLineItemFactory(DjangoModelFactory):
    cart = SubFactory(CartFactory)
    product = SubFactory(ProductFactory)
    quantity = FuzzyInteger(low=1, high=12)
    product_variant = SubFactory(ProductVariantFactory)

    class Meta:
        model = 'carts.CartLineItem'
