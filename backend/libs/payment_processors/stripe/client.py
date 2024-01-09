import stripe
from django.conf import settings
from libs.payment_processors.client import PaymentProcessorClient as BaseClient
from libs.payment_processors.dto import ChargeDTO, PaymentMethodAttachmentDTO, RefundDTO
from libs.payment_processors.exceptions import (
    CouldNotAttachPaymentMethodToProcessorCustomerError,
    CouldNotCreateSetupIntentError,
    CouldNotFetchPaymentMethodError,
    CouldNotFetchProcessorCustomerError,
    CouldNotProcessChargeError,
    CouldNotProcessRefundError,
)


class PaymentProcessorClient(BaseClient):
    def __init__(self, *args, **kwargs):
        self.client = stripe
        self.client.api_key = settings.STRIPE_SECRET_KEY

    @staticmethod
    def _parse_payment_method(payment_method_obj):
        """
		Format payment method fields
		(only date for the time being)
		"""
        card = payment_method_obj.card
        exp_month = f'0{card.exp_month}' if card.exp_month < 10 else f'{card.exp_month}'
        payment_method_obj['expiration_date'] = f'{card.exp_year}-{exp_month}-01'

        return payment_method_obj

    def retrieve_payment_method(self, payment_method):
        try:
            return self._parse_payment_method(
                self.client.PaymentMethod.retrieve(
                    payment_method,
                )
            )
        except stripe.error.APIConnectionError as e:
            raise CouldNotFetchPaymentMethodError(e)

    def create_setup_intent(self, *args, **kwargs):
        try:
            return self.client.SetupIntent.create(**kwargs)
        except (stripe.error.StripeError, stripe.error.APIConnectionError) as e:
            raise CouldNotCreateSetupIntentError(e)

    def create_customer(self, *args, **kwargs):
        return self.client.Customer.create(
            **kwargs
        )

    def retrieve_customer(self, customer):
        try:
            return self.client.Customer.retrieve(
                customer
            )
        except (stripe.error.StripeError, stripe.error.APIConnectionError) as e:
            raise CouldNotFetchProcessorCustomerError(e)

    def charge(self, charge_data: ChargeDTO):
        try:
            return self.client.PaymentIntent.create(
                currency=charge_data.currency_code,
                amount=charge_data.dollar_amount_to_cents(),
                customer=charge_data.processor_customer_id,
                payment_method=charge_data.processor_payment_method_id,
                confirm=charge_data.capture_immediately,
                setup_future_usage='off_session',
            )
        except (stripe.error.CardError, stripe.error.APIConnectionError) as e:
            raise CouldNotProcessChargeError(e)

    def refund(self, refund_data: RefundDTO):
        try:
            return self.client.Refund.create(
                payment_intent=refund_data.processor_transaction_id,
                amount=refund_data.dollar_amount_to_cents(),
                reason=refund_data.reason
            )
        except (stripe.error.CardError, stripe.error.APIConnectionError) as e:
            raise CouldNotProcessRefundError(e)

    def attach_customer_to_payment_method(self, attachment_data: PaymentMethodAttachmentDTO):
        try:
            return self.client.PaymentMethod.attach(
                attachment_data.processor_payment_method_id,
                customer=attachment_data.processor_customer_id
            )
        except (stripe.error.CardError, stripe.error.APIConnectionError) as e:
            raise CouldNotAttachPaymentMethodToProcessorCustomerError(e)
