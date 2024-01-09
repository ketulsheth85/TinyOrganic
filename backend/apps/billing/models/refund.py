from django.db import models

from apps.billing.models import PaymentMethod
from apps.core.models import CoreModel
from apps.customers.models import Customer


class Refund(CoreModel):
    customer = models.ForeignKey(
        to=Customer,
        on_delete=models.PROTECT,
        related_name='refunds',
    )
    payment_method = models.ForeignKey(
        to=PaymentMethod,
        on_delete=models.PROTECT,
        related_name='refunds',
    )
    payment_processor_refund_id = models.CharField(max_length=256)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f'customer: {self.customer}, refund amount: {self.payment_method}'
