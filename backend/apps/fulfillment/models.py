from django.db import models
from localflavor.us.models import USZipCodeField
from apps.core.models import CoreModel


class FulfillmentCenterZipcode(CoreModel):
    zipcode = USZipCodeField(unique=True)

    def __str__(self):
        return f'Fulfillment center zipcode: {self.zipcode}'


class FulfillmentCenter(CoreModel):
    location = models.CharField(max_length=255, unique=True)
    zipcodes = models.ManyToManyField(
        to=FulfillmentCenterZipcode,
        related_name='warehouses'
    )

    def __str__(self):
        return f'Fulfillment center: {self.location}'


