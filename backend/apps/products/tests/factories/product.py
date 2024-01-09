from decimal import Decimal

import factory
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText


class ProductFactory(DjangoModelFactory):
    external_product_id = FuzzyText(prefix='product-id-')
    title = FuzzyText(prefix='title-')
    price = Decimal(1)
    product_type = 'recipe'
    is_active = True

    class Meta:
        model = 'products.Product'

    @factory.post_generation
    def ingredients(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for ingredient in extracted:
                self.ingredients.add(ingredient)


class ProductVariantFactory(DjangoModelFactory):
    product = SubFactory(ProductFactory)
    external_variant_id = FuzzyText(prefix='product-variant-id-')
    price = Decimal(1)
    sku_id = FuzzyText(prefix='sku_id-')

    class Meta:
        model = 'products.ProductVariant'
