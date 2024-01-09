from decimal import Decimal

from django.db import models

from apps.core.models import CoreModel
from apps.customers.models import Customer
from apps.discounts.libs import DiscountRuleTypeEnum
from apps.discounts.models import Discount
from apps.products.models import Product


class Rule(CoreModel):
    discount = models.ForeignKey(
        to=Discount,
        on_delete=models.PROTECT,
        related_name='rules',
    )
    type = models.CharField(max_length=128, choices=DiscountRuleTypeEnum.as_choices())
    apply_to_products = models.ManyToManyField(to=Product, blank=True)
    apply_to_customers = models.ManyToManyField(to=Customer, blank=True)
    minimum_cart_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    nth_time_subscriber = models.SmallIntegerField(null=True, blank=True)
    number_of_orders = models.IntegerField(default=1)
    redemption_limit_per_customer = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.type} - {self.discount}'
