from factory import faker
from factory.django import DjangoModelFactory


class FulfillmentCenterFactory(DjangoModelFactory):
    location = faker.Faker('city')

    class Meta:
        model = 'fulfillment.FulfillmentCenter'


class FulfillmentCenterZipcodeFactory(DjangoModelFactory):
    zipcode = faker.Faker('postcode')

    class Meta:
        model = 'fulfillment.FulfillmentCenterZipcode'
