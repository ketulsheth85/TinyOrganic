from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.billing.models import PaymentProcessor
from apps.customers.models.customer import Customer


class PaymentIntentViewSet(viewsets.ViewSet):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.payment_processor = PaymentProcessor.objects.get(name='Stripe')

	def _create_payment_customer(self, customer):
		payment_processor_customer = self.payment_processor.client.create_customer(
			email=customer.email
		)
		customer.payment_provider_customer_id = payment_processor_customer['id']
		customer.save()

		return customer

	def create(self, request):
		"""
		Creates payment intent for stripe customer, and creates
		stripe customer with customer email if one does not exists.
		Only to be used when Stripe is a the payment provider.
		"""
		data = request.data
		customer_id = data.get('customer')
		customer = Customer.objects.get(id=customer_id)

		if not customer.payment_provider_customer_id:
			self._create_payment_customer(customer)

		# FYI Here we assume the the payment_provider_customer_id id is from stripe
		payment_intent = self.payment_processor.client.create_setup_intent(
			payment_method_types=["card"],
			customer=customer.payment_provider_customer_id,
			usage="off_session",
		)

		return Response(status=status.HTTP_200_OK, data={
			'payment_customer': customer.payment_provider_customer_id,
			'intent': payment_intent['client_secret']
		})
