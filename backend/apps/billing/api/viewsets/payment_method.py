from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.billing.api.serializers.payment_method import (
    PaymentMethodReadOnlySerializer,
    PaymentMethodWriteSerializer,
)
from apps.billing.models import PaymentProcessor
from apps.billing.models.payment_method import PaymentMethod
from apps.customers.models.customer import Customer


class PaymentMethodViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
	queryset = PaymentMethod.objects.filter()
	serializers_class = PaymentMethodReadOnlySerializer

	def get_serializer_class(self):
		if self.request.method == 'POST':
			return PaymentMethodWriteSerializer

		return PaymentMethodReadOnlySerializer

	def create(self, request):
		"""
		We currently only support credit card payment_processors, if we want to support other payment types,
		we would have to update the create method and the payment method model
		"""
		data = request.data
		customer_id = data.get('customer')
		payment_method_id = data.get('payment_method')
		payment_processor = PaymentProcessor.objects.get(name='Stripe')

		created = False
		try:
			payment_method = PaymentMethod.objects.get(
				payment_processor=payment_processor,
				payment_processor_payment_method_id=payment_method_id,
				customer_id=customer_id
			)
		except PaymentMethod.DoesNotExist:
			customer = Customer.objects.get(
				id=customer_id,
			)
			payment_method_response = payment_processor.client.retrieve_payment_method(
				payment_method_id,
			)

			card = payment_method_response['card']
			exp_month = f'0{card["exp_month"]}' if card["exp_month"] < 10 else f'{card["exp_month"]}'
			expiration_date = f'{card["exp_year"]}-{exp_month}-01'

			payment_method = PaymentMethod.objects.create(
				customer=customer,
				payment_processor=payment_processor,
				payment_processor_payment_method_id=payment_method_id,
				last_four=payment_method_response['card']['last4'],
				expiration_date=expiration_date,
			)
			created = True
		payment_method.attach_to_payment_processor_customer()
		payment_method.setup_for_future_charges = True
		payment_method.is_valid = True
		payment_method.save()

		return Response(
			self.serializers_class(payment_method).data,
			status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
		)

	@action(methods=['GET'], detail=False)
	def latest(self, request):
		customer = self.request.query_params.get('customer')

		payment_method = None
		try:
			payment_method = PaymentMethod.objects.filter(customer=customer)\
				.latest('created_at')
		except PaymentMethod.DoesNotExist:
			return Response({'detail': 'no valid payment method exists for this user'}, status.HTTP_404_NOT_FOUND)

		serialized_payment_method = PaymentMethodReadOnlySerializer(payment_method).data

		return Response(serialized_payment_method, status=status.HTTP_200_OK)
