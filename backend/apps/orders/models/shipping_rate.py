from django.db import models

from apps.core.models import CoreModel


class ShippingRate(CoreModel):
    title = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} - ${self.price}'
