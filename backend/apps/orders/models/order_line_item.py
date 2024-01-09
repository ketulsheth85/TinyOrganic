from django.db import models

from apps.core.models import CoreModel
from apps.orders.models import Order
from apps.products.models import Product, ProductVariant


class OrderLineItem(CoreModel):
    order = models.ForeignKey(
        to=Order,
        on_delete=models.PROTECT,
        related_name='line_items',
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.PROTECT,
    )
    product_variant = models.ForeignKey(
        to=ProductVariant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'{self.order}: {self.product} x {self.quantity}'
