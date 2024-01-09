from factory import SubFactory, faker
from factory.django import DjangoModelFactory

from apps.customers.tests.factories import CustomerFactory


class LocationFactory(DjangoModelFactory):
    customer = SubFactory(CustomerFactory)
    street_address = faker.Faker('address')
    city = faker.Faker('city')
    state = 'FL'
    zipcode = faker.Faker('postcode')
    is_active = False

    class Meta:
        model = 'addresses.Location'
