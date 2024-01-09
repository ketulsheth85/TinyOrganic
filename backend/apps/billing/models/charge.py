from django.db import models
from model_utils import Choices

from apps.billing.models import PaymentMethod
from apps.core.models import CoreModel
from apps.customers.models import Customer


class ChargeStatusEnum:
    captured = 'captured'
    uncaptured = 'uncaptured'


class Charge(CoreModel):
    customer = models.ForeignKey(
        to=Customer,
        on_delete=models.PROTECT,
        related_name='charges',
    )
    payment_method = models.ForeignKey(
        to=PaymentMethod,
        on_delete=models.PROTECT,
        related_name='charges',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_processor_charge_id = models.CharField(max_length=256)
    status = models.CharField(
        max_length=128,
        choices=Choices(ChargeStatusEnum.captured, ChargeStatusEnum.uncaptured),
        default=ChargeStatusEnum.uncaptured,
    )

    def __str__(self) -> str:
        return f'customer: {self.customer}, amount: {self.payment_method}, {self.status}'
