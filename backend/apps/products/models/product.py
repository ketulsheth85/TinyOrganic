from decimal import Decimal

from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction

# Create your models here.
from django.db.models import DateField

from apps.core.models import CoreModel
from apps.fulfillment.models import FulfillmentCenter
from apps.products.tasks import replace_product_in_cart_line_items_for_active_subscribers
from apps.recipes.models import Ingredient


class Product(CoreModel):
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    tags = ArrayField(base_field=models.CharField(max_length=256), default=list, null=True)
    external_product_id = models.CharField(max_length=256, null=True, blank=True)
    image_url = models.TextField(blank=True)
    featured_recipe_image_url = models.TextField(blank=True, null=True)
    price = models.DecimalField(default=Decimal('0'),max_digits=10,decimal_places=2)
    is_active = models.BooleanField(default=False)
    product_type = models.CharField(max_length=128, null=True, blank=True)
    metadata = models.JSONField(default=dict, null=True, blank=True)
    ingredients = models.ManyToManyField(to=Ingredient, blank=True,)
    featured_ingredients = models.TextField(blank=True)
    deactivation_date: DateField = models.DateField(null=True, blank=True)
    reactivation_date = models.DateField(null=True, blank=True)
    nutrition_image_url = models.URLField(blank=True, null=True)
    from_production_shopify_store = models.BooleanField(default=False)
    show_variants = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=True)
    fulfillment_centers = models.ManyToManyField(
        to=FulfillmentCenter,
        related_name='fulfillment_products'
    )

    def __str__(self):
        return f'{self.title} - {self.product_type}'

    def _replace_cart_line_items_containing_product(self):
        replace_product_in_cart_line_items_for_active_subscribers.delay(
            self.id)

    def save(self, *args, **kwargs):
        if 'is_active' in self.get_dirty_fields() and not self.is_active:
            transaction.on_commit(
                self._replace_cart_line_items_containing_product)

        super().save(*args, **kwargs)


class ProductVariant(CoreModel):
    title = models.CharField(max_length=256, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='variants')
    external_variant_id = models.CharField(max_length=256, null=True, blank=True)
    sku_id = models.CharField(max_length=256, null=True, blank=True)
    price = models.DecimalField(default=Decimal('0'), max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product} - {self.sku_id}'
