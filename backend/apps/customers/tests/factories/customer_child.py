import factory
from django.utils import timezone
from factory import SubFactory, faker, lazy_attribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from apps.customers.tests.factories import CustomerFactory


class CustomerChildFactory(DjangoModelFactory):
    first_name = faker.Faker('first_name')
    last_name = faker.Faker('last_name')
    parent = SubFactory(CustomerFactory)
    sex = FuzzyChoice(choices=('male', 'female'))
    cart = None

    @lazy_attribute
    def birth_date(self):
        return timezone.now().date()

    class Meta:
        model = 'customers.CustomerChild'

    @factory.post_generation
    def allergies(self, created, extracted, **kwargs):
        if not created:
            return

        if extracted:
            for allergy in extracted:
                self.allergies.add(allergy)
