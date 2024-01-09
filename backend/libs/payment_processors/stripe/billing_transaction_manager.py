from django.apps import apps
from libs.payment_processors.billing_transaction_manager import (
    BillingTransactionManager as BaseTransactionManager,
)


class BillingTransactionManager(BaseTransactionManager):
    def save_charge_to_database(self):
        Charge = apps.get_model('billing', 'Charge')

        return Charge.objects.create(
            customer_id=self.processed_charge_data.customer_id,
            payment_method_id=self.processed_charge_data.payment_method_id,
            payment_processor_charge_id=self.processed_charge_data.processor_transaction_id,
            amount=self.processed_charge_data.cents_amount_to_decimal_amount(),
            status='captured' if self.processed_charge_data.is_captured else 'uncaptured',
        )

    def save_refund_to_database(self):
        Refund = apps.get_model('billing', 'Refund')

        return Refund.objects.create(
            customer_id=self.processed_refund_data.customer_id,
            payment_method_id=self.processed_refund_data.customer_payment_method_id,
            amount=self.processed_refund_data.cents_amount_to_decimal_amount(),
            payment_processor_refund_id=self.processed_refund_data.processor_transaction_id
        )
