from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils.functional import cached_property

from apps.core.models import CoreModel
from apps.customers.models import Customer, CustomerChild


class Cart(CoreModel):
    customer = models.ForeignKey(
        to=Customer,
        on_delete=models.PROTECT,
        related_name='carts',
    )
    customer_child = models.OneToOneField(
        to=CustomerChild,
        on_delete=models.PROTECT,
        related_name='cart',
        null=True,
    )

    def __str__(self):
        return f'{self.customer_child}'

    @property
    def subtotal(self):
        return sum([
            Decimal(f'{line_item.product_variant.price}') * line_item.quantity for line_item in self.line_items.filter()
        ])

    @cached_property
    def most_popular_line_item(self):
        return self.line_items.filter().order_by('-quantity').first()

    def number_of_recipe_servings(self):
        return self.line_items.filter(product__product_type__iexact='recipe').aggregate(
            Sum('quantity')
        )['quantity__sum']

    def total_quantity_of_items(self):
        return self.line_items.filter().exclude(
            product__product_type__icontains='add'
        ).aggregate(
            Sum('quantity')
        )['quantity__sum']

    @property
    def subtotal(self):
        return sum([
            Decimal(f'{line_item.product_variant.price}') * line_item.quantity for line_item in self.line_items.filter()
        ])

    def remove_onetime_line_items(self):
        return self.line_items.filter(product__is_recurring=False).delete()
