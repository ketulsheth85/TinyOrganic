import uuid
from unittest import mock

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.billing.models import PaymentProcessor
from apps.billing.tests.factories import PaymentProcessorFactory
from apps.billing.tests.factories.payment_method import PaymentMethodFactory
from apps.customers.tests.factories.customer import CustomerFactory
from apps.orders.tests.factories import ShippingRateFactory


def _mock_get_payment_method(payment_method, *args):
    return {
        'id': payment_method,
        'payment_method': str(uuid.uuid4),
        'customer': 'PaymentMethodViewSetTestCase_stripe_customer_id',
		'card': {
			'last4': 1234,
			'exp_month': 1,
			'exp_year': 2040
		}
    }


def _mock_create_payment_intent(*args,**kwargs):
    return {
        'id': 'payment_intent_id',
        'client_secret': 'el_secreto'
    }


def _mock_create_stripe_customer(*args,**kwargs):
    return {
        'id': f'{kwargs["email"]}-id',
        'email': kwargs['email']
    }


def _mock_attach_payment_method_to_customer(*args, **kwargs):
    return True


class PaymentMethodViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.customer = CustomerFactory(
            payment_provider_customer_id='PaymentMethodViewSetTestCase_stripe_customer_id'
        )

    def setUp(self) -> None:
        ShippingRateFactory()
        PaymentProcessorFactory(name='Stripe')

    def test_responds_with_201_status_code_when_creating_new_payment_method(self):
        customer = self.customer
        url = reverse('payment-method-list')
        with mock.patch(
            'libs.payment_processors.stripe.client.PaymentProcessorClient.retrieve_payment_method',
            side_effect=_mock_get_payment_method
        ):
            with mock.patch(
                'apps.billing.models.payment_method.PaymentMethod.attach_to_payment_processor_customer',
                side_effect=_mock_attach_payment_method_to_customer,
            ):
                response = self.client.post(url, {
                  'customer': str(customer.id),
                  'payment_method': 'fake_payment_method_id'
                })
                self.assertEquals(response.status_code, 201)

    def test_responds_with_200_status_code_when_creating_and_payment_method_already_exists(self):
        payment_method = PaymentMethodFactory(
            customer=self.customer,
            payment_processor=PaymentProcessor.objects.first(),
        )
        url = reverse('payment-method-list')
        with mock.patch(
            'libs.payment_processors.stripe.client.PaymentProcessorClient.retrieve_payment_method',
            side_effect=_mock_get_payment_method
        ):
            with mock.patch(
                'apps.billing.models.payment_method.PaymentMethod.attach_to_payment_processor_customer',
                side_effect=_mock_attach_payment_method_to_customer,
            ):
                response = self.client.post(url, {
                  'customer': str(self.customer.id),
                  'payment_method': str(payment_method.id)
                })
                self.assertEquals(response.status_code, 201)

    def test_responds_with_200_when_creating_payment_intent(self):
        url = reverse('payment-intent-list')
        with mock.patch(
            'libs.payment_processors.stripe.client.PaymentProcessorClient.create_setup_intent',
            side_effect=_mock_create_payment_intent
        ):
            response = self.client.post(url, {
                'customer': str(self.customer.id),
                'items': [{'id': 'expensive-meal'}]
            })
            self.assertEquals(response.status_code, 200)
            self.assertEquals(response.json()['intent'], 'el_secreto')

    def test_responds_with_200_when_creating_setup_intent_for_customer_with_no_payment_customer_field(self):
        customer = CustomerFactory(email="rich@guy.com")
        url = reverse('payment-intent-list')
        with mock.patch(
            'libs.payment_processors.stripe.client.PaymentProcessorClient.create_setup_intent',
            side_effect=_mock_create_payment_intent
        ):
            with mock.patch(
                'libs.payment_processors.stripe.client.PaymentProcessorClient.create_customer',
                side_effect=_mock_create_stripe_customer
            ):
                response = self.client.post(url,{
                    'customer': str(customer.id),
                    'items': [{'id': 'expensive-meal'}]
                })
                self.assertEquals(response.status_code, 200)
                self.assertEquals(response.json()['intent'], 'el_secreto')

    def test_responds_with_200_when_fetching_latest_payment_method(self):
        customer = CustomerFactory(email="señortiny@exec.com")
        customer_payment_method = PaymentMethodFactory(
            customer=customer,
            payment_processor=PaymentProcessor.objects.first(),
        )
        base_url = reverse('payment-method-latest')
        response = self.client.get(f'{base_url}?customer={customer.id}')
        latest_payment_method = response.json()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(latest_payment_method.get('id'), str(customer_payment_method.id))

    def test_responds_with_200_when_fetching_latest_payment_method_and_user_has_multiple_payment_methods(self):
        customer = CustomerFactory(email="user_with_several_credit_cards")
        PaymentMethodFactory(
            customer=customer,
            payment_processor=PaymentProcessor.objects.first(),
        )
        expected_latest_payment_method = PaymentMethodFactory(
            customer=customer,
            payment_processor=PaymentProcessor.objects.first(),
        )
        base_url = reverse('payment-method-latest')
        response = self.client.get(f'{base_url}?customer={customer.id}')
        latest_payment_method = response.json()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(latest_payment_method.get('id'), str(expected_latest_payment_method.id))
