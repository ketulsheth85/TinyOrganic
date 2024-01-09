import stripe

from settings.minimal import env


class StripeImportClient:
    def __init__(self):
        self.client = stripe
        self.client.api_key = env.str('MAIN_STORE_STRIPE_API_KEY', default='FAKE')

    def get_customer_with_email(self, email: str):
        return self.client.Customer.list(limit=1, email=email)

    def get_payment_method_with_stripe_customer_id(self, stripe_customer_id: str):
        return self.client.PaymentMethod.list(limit=1, type='card', customer=stripe_customer_id)

    def create_setupintent_with_payment_method_id(self, payment_method_id: str, stripe_customer_id: str = ''):
        return self.client.SetupIntent.create(
            confirm=True,
            customer=stripe_customer_id,
            payment_method=payment_method_id,
            payment_method_types=['card', ],
            usage='off_session',
            metadata={'created_by': 'Import to Re-platform Method.'}
        )

    def create_refund(self, refund_dto: 'RefundDTO'):
        return self.client.Refund.create(**refund_dto)
