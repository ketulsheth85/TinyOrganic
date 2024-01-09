from django.db import models

from apps.core.models import CoreModel


class BaseNameModel(CoreModel):
    name = models.TextField(unique=True)

    class Meta(CoreModel.Meta):
        abstract = True

    def __str__(self) -> str:
        return f'{self.name}'


class Ingredient(BaseNameModel):
    ...
