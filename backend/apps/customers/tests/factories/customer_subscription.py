from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from apps.customers.tests.factories import CustomerChildFactory, CustomerFactory


class CustomerSubscriptionFactory(DjangoModelFactory):
    customer = SubFactory(CustomerFactory)
    customer_child = SubFactory(CustomerChildFactory)
    number_of_servings = FuzzyChoice(choices=(12, 24,))
    frequency = FuzzyChoice(choices=(1, 2, 4))

    class Meta:
        model = 'customers.CustomerSubscription'
