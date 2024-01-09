import uuid
from decimal import Decimal
from unittest import mock

from django.test import TestCase

from apps.billing.tests.factories import PaymentMethodFactory, PaymentProcessorFactory
from apps.orders.tests.factories import OrderFactory


def _mock_attach_to_payment_processor_customer(*args, **kwargs):
    return True


def _mock_charge(*args, **kwargs):
    class MockProcessedCharge:
        id = f'{uuid.uuid4()}'
        status = 'succeeded'
        amount = 1000

    return MockProcessedCharge()


class PaymentMethodModelTestSuite(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.payment_method = PaymentMethodFactory()

    def test_saves_related_payment_processor_charge_to_database(self):
        processed_charge = _mock_charge()
        self.payment_method._save_related_charge_to_db(processed_charge)

        self.assertTrue(self.payment_method.charges.filter(payment_processor_charge_id=processed_charge.id).exists())

    def test_calls_the_payment_processor_client_to_capture_a_charge(self):
        with mock.patch(
            'libs.payment_processors.stripe.client.PaymentProcessorClient.charge',
            side_effect=_mock_charge,
        ) as mocked:
            self.payment_method.charge(Decimal('10'))
        self.assertTrue(mocked.called)

    def test_replaces_order_payment_method_after_new_payment_method_becomes_valid(self):
        order = OrderFactory(customer=self.payment_method.customer, payment_method=self.payment_method)
        new_payment_method = PaymentMethodFactory(customer=self.payment_method.customer)
        new_payment_method.is_valid = True
        new_payment_method.setup_for_future_charges = True
        with self.captureOnCommitCallbacks(execute=True):
            new_payment_method.save()

        order.refresh_from_db()
        self.assertEqual(order.payment_method.id, new_payment_method.id)


class PaymentProcessorModelTestSuite(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.payment_processor = PaymentProcessorFactory()

    def test_cannot_fetch_api_client_if_not_active(self):
        self.payment_processor.is_active = False
        self.payment_processor.save()
        self.assertIsNone(self.payment_processor.client)

    def test_cannot_fetch_charge_manager_if_not_active(self):
        self.payment_processor.is_active = False
        self.payment_processor.save()
        self.assertIsNone(self.payment_processor.billing_transaction_manager)
