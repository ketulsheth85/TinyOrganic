from django.contrib import admin
from django.contrib.admin import register

from apps.recipes.models import Ingredient


@register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    ...
