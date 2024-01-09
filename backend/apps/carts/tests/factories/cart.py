from factory import SubFactory
from factory.django import DjangoModelFactory

from apps.customers.tests.factories import CustomerChildFactory, CustomerFactory


class CartFactory(DjangoModelFactory):
    customer = SubFactory(CustomerFactory)
    customer_child = SubFactory(CustomerChildFactory)

    class Meta:
        model = 'carts.Cart'
