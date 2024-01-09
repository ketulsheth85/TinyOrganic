from decimal import Decimal
from unittest import mock

import stripe
from django.test import SimpleTestCase
from libs.payment_processors.dto import ChargeDTO, PaymentMethodAttachmentDTO, RefundDTO
from libs.payment_processors.exceptions import (
    CouldNotAttachPaymentMethodToProcessorCustomerError,
    CouldNotCreateSetupIntentError,
    CouldNotFetchPaymentMethodError,
    CouldNotFetchProcessorCustomerError,
    CouldNotProcessChargeError,
    CouldNotProcessRefundError,
)
from libs.payment_processors.stripe import PaymentProcessorClient


def _mock_force_connection_error_exception(*args, **kwargs):
    raise stripe.error.APIConnectionError("A connection issue")


class StripePaymentProcessorAPIClientTestSuite(SimpleTestCase):
    def test_will_raise_error_if_connection_error_happens_when_fetching_payment_method(self):
        with mock.patch(
            'stripe.api_resources.abstract.api_resource.APIResource.retrieve',
            side_effect=_mock_force_connection_error_exception,
        ):
            with self.assertRaises(CouldNotFetchPaymentMethodError):
                PaymentProcessorClient().retrieve_payment_method({})

    def test_will_raise_error_if_connection_error_happens_when_charging_card(self):
        with mock.patch(
            'stripe.api_resources.abstract.createable_api_resource.CreateableAPIResource.create',
            side_effect=_mock_force_connection_error_exception,
        ):
            with self.assertRaises(CouldNotProcessChargeError):
                PaymentProcessorClient().charge(
                    ChargeDTO(
                        decimal_amount=Decimal('10'),
                        processor_customer_id='customer',
                        processor_payment_method_id='payment_method'
                    )
                )

    def test_will_raise_error_if_connection_error_happens_when_attaching_payment_method_to_customer(self):
        with mock.patch(
            'stripe.api_resources.payment_method.PaymentMethod.attach',
            side_effect=_mock_force_connection_error_exception,
        ):
            with self.assertRaises(CouldNotAttachPaymentMethodToProcessorCustomerError):
                PaymentProcessorClient().attach_customer_to_payment_method(
                    PaymentMethodAttachmentDTO(processor_customer_id='str', processor_payment_method_id='str')
                )

    def test_will_raise_error_if_connection_error_happens_when_creating_setup_intent(self):
        with mock.patch(
            'stripe.api_resources.abstract.createable_api_resource.CreateableAPIResource.create',
            side_effect=_mock_force_connection_error_exception,
        ):
            with self.assertRaises(CouldNotCreateSetupIntentError):
                PaymentProcessorClient().create_setup_intent({})

    def test_will_raise_error_if_connection_error_happens_when_fetching_customer(self):
        with mock.patch(
            'stripe.api_resources.abstract.api_resource.APIResource.retrieve',
            side_effect=_mock_force_connection_error_exception,
        ):
            with self.assertRaises(CouldNotFetchProcessorCustomerError):
                PaymentProcessorClient().retrieve_customer({})

    def test_will_raise_error_if_connection_error_happens_when_creating_refund(self):
        with mock.patch(
            'stripe.api_resources.abstract.createable_api_resource.CreateableAPIResource.create',
            side_effect=_mock_force_connection_error_exception,
        ):
            with self.assertRaises(CouldNotProcessRefundError):
                PaymentProcessorClient().refund(
                    RefundDTO(
                        processor_transaction_id='1',
                        reason='requested_by_customer',
                        decimal_amount=Decimal('10'),
                    )
                )
