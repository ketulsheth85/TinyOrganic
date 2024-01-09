from typing import List

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition
from model_utils import Choices
from django_softdelete.models import SoftDeleteModel

from apps.core.models import CoreModel
from apps.customers.models import Customer, CustomerChild
from apps.discounts.libs import DiscountRuleTypeEnum, CustomerDiscountStatusEnum


class Discount(CoreModel):
    codename = models.CharField(max_length=128)
    referrer = models.ForeignKey(
        to=Customer,
        on_delete=models.PROTECT,
        related_name='referral_discount_codes',
        blank=True,
        null=True,
    )
    discount_type = models.CharField(
        max_length=128,
        choices=Choices('percentage', 'fixed amount'),
        default='percentage',
    )
    from_yotpo = models.BooleanField(default=False)
    from_brightback = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    banner_text = models.TextField(blank=True)
    redemption_limit = models.PositiveBigIntegerField(null=True, blank=True)
    redemption_count = models.BigIntegerField(default=0)
    redemption_limit_per_customer = models.PositiveSmallIntegerField(default=1)
    activate_at = models.DateTimeField(null=True, blank=True)
    deactivate_at = models.DateTimeField(null=True, blank=True)

    deactivated_at = models.DateTimeField(null=True, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if self.discount_type == 'percentage':
            amount_off = f'{self.amount}%'
        else:
            amount_off = f'${self.amount}'
        return f'{self.codename}, {amount_off} off orders'

    def save(self, *args, **kwargs):
        if 'is_active' in self.get_dirty_fields():
            if self.is_active:
                self.activated_at = timezone.now()
            elif not self.is_new() and not self.is_active:
                self.deactivated_at = timezone.now()

        super().save(*args, **kwargs)


class CustomerDiscount(CoreModel, SoftDeleteModel):
    discount = models.ForeignKey(
        to=Discount,
        on_delete=models.PROTECT,
    )
    customer = models.ForeignKey(
        to=Customer,
        on_delete=models.PROTECT,
        related_name='discounts',
    )
    customer_child = models.ForeignKey(
        to=CustomerChild,
        on_delete=models.PROTECT,
        related_name='assigned_discounts',
        null=True,
        blank=False,
    )
    status = FSMField(
        choices=Choices(
            CustomerDiscountStatusEnum.unredeemed,
            CustomerDiscountStatusEnum.redeemed
        ),
        default=CustomerDiscountStatusEnum.unredeemed,
    )
    applied_at = models.DateTimeField(null=True, blank=True)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    redemption_limit = models.PositiveSmallIntegerField(default=1)
    redemption_count = models.SmallIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    @transition(
        field='status',
        source=[CustomerDiscountStatusEnum.unredeemed, CustomerDiscountStatusEnum.redeemed],
        target=CustomerDiscountStatusEnum.redeemed,
        on_error=CustomerDiscountStatusEnum.unredeemed,
    )
    def redeem(self):
        self.redemption_count += 1
        self.redeemed_at = timezone.now()

    def get_product_discount_rule(self):
        return self.discount.rules.filter(is_active=True, type=DiscountRuleTypeEnum.product).first()

    def __str__(self):
        return f'{self.discount}, {self.status} by {self.customer}'

    class Meta(CoreModel.Meta):
        ordering = 'created_at', 'modified_at',

    def save(self, *args, **kwargs):
        if 'status' in self.get_dirty_fields() and self.status == CustomerDiscountStatusEnum.redeemed:
            if self.redemption_count >= self.redemption_limit:
                self.is_active = False

        super().save(*args, **kwargs)
