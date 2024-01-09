from datetime import timedelta
from decimal import Decimal

from django.apps import apps
from django.db import models, transaction
from django.utils import timezone

from apps.orders.libs import OrderPaymentStatusEnum
from libs.payment_processors.dto import (
    ChargeDTO,
    PaymentMethodAttachmentDTO,
    ProcessedChargeDTO,
    ProcessedRefundDTO,
    RefundDTO,
)
from libs.payment_processors.exceptions import CouldNotChargeOrderError, CouldNotProcessRefundError, \
    CouldNotProcessChargeError

from apps.billing.models import PaymentProcessor
from apps.core.models import CoreModel
from apps.customers.models import Customer


class PaymentMethod(CoreModel):
    customer = models.ForeignKey(
        to=Customer,
        on_delete=models.PROTECT,
        related_name='payment_methods',
    )
    payment_processor = models.ForeignKey(
        to=PaymentProcessor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    payment_processor_payment_method_id = models.TextField(unique=True)
    last_four = models.TextField()
    expiration_date = models.DateField(null=True, blank=True)
    is_valid = models.BooleanField(default=False)
    setup_for_future_charges = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.customer.email}, {self.payment_processor_payment_method_id}'

    def attach_to_payment_processor_customer(self):
        attachment_data = PaymentMethodAttachmentDTO(
            processor_customer_id=f'{self.customer.payment_provider_customer_id}',
            processor_payment_method_id=f'{self.payment_processor_payment_method_id}',
        )
        return self.payment_processor.client.attach_customer_to_payment_method(attachment_data)

    def _save_related_charge_to_db(self, processed_charge):
        charge_data = ProcessedChargeDTO(
            customer_id=f'{self.customer.id}',
            payment_method_id=self.id,
            cents_amount=processed_charge.amount,
            processor_transaction_id=processed_charge.id,
            is_captured=processed_charge.status == 'succeeded'
        )
        return self.payment_processor.billing_transaction_manager(
            processed_charge_dto=charge_data
        ).save_charge_to_database()

    def charge(self, amount: Decimal):
        """
        Handles the charging of the payment method.
        We create an idempotent key to ensure that payment charges that were processed
        on the payment provider's end do not get re-processed.
        Thus, preventing customers from being charged n-times.
        """
        try:
            charge_data = ChargeDTO(
                processor_customer_id=f'{self.customer.payment_provider_customer_id}',
                processor_payment_method_id=f'{self.payment_processor_payment_method_id}',
                decimal_amount=amount,
            )
            payment_processor_charge = self.payment_processor.client.charge(charge_data)
            return self._save_related_charge_to_db(processed_charge=payment_processor_charge)
        except (CouldNotChargeOrderError, CouldNotProcessChargeError):
            raise

    def _save_related_refund_to_db(self, processed_refund):
        refund_dto = ProcessedRefundDTO(
            processor_transaction_id=processed_refund.id,
            customer_id=f'{self.customer.id}',
            cents_amount=processed_refund.amount,
            customer_payment_method_id=self.id,
        )
        return self.payment_processor.billing_transaction_manager(
            processed_refund_dto=refund_dto
        ).save_refund_to_database()

    def refund(self, amount: Decimal, processor_charge_id: str):
        """
        Handles refunding to payment method
        """
        try:
            refund_data = RefundDTO(
                decimal_amount=amount,
                processor_transaction_id=processor_charge_id,
            )
            payment_processor_refund = self.payment_processor.client.refund(refund_data)
            return self._save_related_refund_to_db(payment_processor_refund)
        except CouldNotProcessRefundError:
            raise

    def _update_pending_orders_with_payment_method(self):
        Order = apps.get_model('orders', 'Order')
        pending_orders = Order.objects.filter(
            customer=self.customer,
            payment_status=str(OrderPaymentStatusEnum.pending),
            created_at__date__gte=timezone.now().date() - timedelta(days=10),
        ).distinct('customer_child')
        for order in pending_orders:
            order.payment_method = self
            order.save()

    def save(self, *args, **kwargs):
        changed_fields = self.get_dirty_fields()
        if 'setup_for_future_charges' in changed_fields:
            if self.is_valid and self.setup_for_future_charges:
                transaction.on_commit(self._update_pending_orders_with_payment_method)

        super().save(*args, **kwargs)
