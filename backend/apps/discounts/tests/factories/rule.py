import factory
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyInteger

from apps.discounts.tests.factories import DiscountFactory


class RuleFactory(DjangoModelFactory):
    discount = SubFactory(DiscountFactory)
    type = FuzzyChoice(
        choices=(
            'Minimum Price',
            'Product',
            'Number of Orders',
            'Customer Set',
            'Nth-time Subscribers',
            'Redemption Limit per Customer',
        ),
    )
    nth_time_subscriber = FuzzyInteger(low=1, high=3)

    class Meta:
        model = 'discounts.Rule'

    @factory.post_generation
    def apply_to_products(self, created, extracted, **kwargs):
        if not created:
            return

        if extracted:
            for product in extracted:
                self.apply_to_products.add(product)

    @factory.post_generation
    def apply_to_customers(self, created, extracted, **kwargs):
        if not created:
            return

        if extracted:
            for customer in extracted:
                self.apply_to_customers.add(customer)
