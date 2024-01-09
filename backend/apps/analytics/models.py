from django.db import models

from apps.core.models import CoreModel


class Pixel(CoreModel):
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=False)
    tag_script = models.TextField(blank=True)

    def __str__(self):
        return f'{self.name}'
