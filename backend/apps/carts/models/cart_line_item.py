from django.db import models

from apps.carts.models import Cart
from apps.core.models import CoreModel
from apps.products.models import Product, ProductVariant


class CartLineItem(CoreModel):
    cart = models.ForeignKey(
        to=Cart,
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
        return f'{self.cart}, {self.product_variant} x {self.quantity}'
