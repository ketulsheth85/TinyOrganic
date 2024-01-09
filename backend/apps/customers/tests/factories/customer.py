import uuid

from factory import faker, lazy_attribute
from factory.django import DjangoModelFactory


class CustomerFactory(DjangoModelFactory):
    first_name = faker.Faker('first_name')
    last_name = faker.Faker('last_name')
    
    class Meta:
        model = 'customers.Customer'

    @lazy_attribute
    def email(self) -> str:
        return f'{uuid.uuid4()}@tinyorganics-test.com'
