from unittest import mock

from django.test import TestCase

from libs.yotpo_client import (
    YotpoClient,
    CouldNotUpdateYotpoCustomerError,
    CouldNotGetYotpoCustomerError,
    CouldNotCreateYotpoCustomerError,
    CouldNotCreateYotpoOrderError,
    CouldNotCreateYotpoRefundError,
    LoyaltyProgramCustomer,
    LoyaltyProgramOrder,
    LoyaltyProgramItem,
    LoyaltyProgramRefund,
)
from libs import api_request


def _mock_create_loyalty_program_client(*args, **kwargs):
    class MockLoyaltyProgramClient:
        status_code = 200

        def json(self):
            return {}

    return MockLoyaltyProgramClient()


def _mock_get_loyalty_program_client_response(*args, **kwargs):
    class MockLoyaltyProgramClientResponse:
        status_code = 200

        def json(self):
            return {
                'email': 'customer@email.com',
                'referral_code': {
                    'code': '12345'
                }
            }

    return MockLoyaltyProgramClientResponse()

def _mock_create_loyalty_program_client_error_response(*args, **kwargs):
    raise CouldNotCreateYotpoCustomerError


def _mock_update_loyalty_customer_error_response(*args, **kwargs):
    raise CouldNotUpdateYotpoCustomerError


def _mock_get_loyalty_customer_error_response(*args, **kwargs):
    raise CouldNotGetYotpoCustomerError


def _mock_create_loyalty_order_success_response_object(*args, **kwargs):
    class CreateLoyaltyOrderResponse:
        status_code = 200
        parsed_body = {}
        response = None

        def set_response(self):
            self.response = CreateLoyaltyOrderResponse()
            return self

    return CreateLoyaltyOrderResponse().set_response()


def _mock_create_loyalty_order_error_response_object(*args, **kwargs):
    class LoyaltyOrderErrorResponse:
        status_code = 400
        parsed_body = {}
        response = None

        def set_response(self):
            self.response = LoyaltyOrderErrorResponse()
            return self

    return LoyaltyOrderErrorResponse().set_response()


def _mock_create_loyalty_refund_success_response_object(*args, **kwargs):
    class LoyaltyRefundResponse:
        status_code = 200
        parsed_body = {}
        response = None

        def set_response(self):
            self.response = LoyaltyRefundResponse()
            return self

    return LoyaltyRefundResponse().set_response()


def _mock_create_loyalty_refund_error_response_object(*args, **kwargs):
    class LoyaltyRefundErrorResponse:
        status_code = 400
        parsed_body = {}
        response = None

        def set_response(self):
            self.response = LoyaltyRefundErrorResponse()
            return self

    return LoyaltyRefundErrorResponse().set_response()


class YotpoClientTestSuite(TestCase):
    def setUp(self) -> None:
        self.client = YotpoClient()
        self.customer_data = LoyaltyProgramCustomer(
            id='12344',
            email='fake@email.com',
            first_name='fake',
            last_name='also-fake'
        )
        self.order_data = LoyaltyProgramOrder(
            customer_email='fake@email.com',
            total_amount_cents=100,
            currency_code='USD',
            order_id='1234',
            status='paid',
            coupon_code='fake',
            ignore_ip_ua=True,
            discount_amount_cents=0,
            items=[LoyaltyProgramItem(
                name='fake food',
                price_cents=100,
                vendor='Tiny Organics inc',
                id='1234',
                type='food',
                quantity=1,
                collections='fake collection'
            ).to_dict()]
        )
        self.refund_data = LoyaltyProgramRefund(
            order_id='1234',
            total_amount_cents=100,
            currency='USD',
        )

    def test_can_get_yotpo_customer(self):
        with mock.patch(
            'libs.yotpo_client.YotpoClient.get_customer',
            side_effect=_mock_get_loyalty_program_client_response,
        ) as mocked:
            self.client.get_customer(self.customer_data.id)
        self.assertTrue(mocked.called)

    def test_create_yotpo_customer(self):
        with mock.patch(
            'libs.yotpo_client.YotpoClient.create_customer',
            side_effect=_mock_create_loyalty_program_client,
        ) as mocked:
            self.client.create_customer(self.customer_data)
        self.assertTrue(mocked.called)

    def test_can_update_yotpo_customer(self):
        with mock.patch(
            'libs.yotpo_client.YotpoClient.update_customer',
            side_effect=_mock_create_loyalty_program_client,
        ) as mocked:
            self.client.update_customer(self.customer_data)
        self.assertTrue(mocked.called)

    def test_will_raise_error_when_customer_creation_fails(self):
        with mock.patch(
            'libs.yotpo_client.YotpoClient.create_customer',
            side_effect=_mock_create_loyalty_program_client_error_response,
        ):
            with self.assertRaises(CouldNotCreateYotpoCustomerError):
                self.client.create_customer(self.customer_data)

    def test_will_raise_error_when_customer_update_fails(self):
        with mock.patch(
            'libs.yotpo_client.YotpoClient.update_customer',
            side_effect=_mock_update_loyalty_customer_error_response,
        ):
            with self.assertRaises(CouldNotUpdateYotpoCustomerError):
                self.client.update_customer(self.customer_data)

    def test_will_raise_error_when_customer_get_fails(self):
        with mock.patch(
            'libs.yotpo_client.YotpoClient.get_customer',
            side_effect=_mock_get_loyalty_customer_error_response,
        ):
            with self.assertRaises(CouldNotGetYotpoCustomerError):
                self.client.get_customer(self.customer_data.id)

    def test_create_yotpo_order(self):
        with mock.patch(
                'libs.api_request.make_logged_api_request',
                side_effect=_mock_create_loyalty_order_success_response_object,
        ) as mocked:
            self.client.create_order(self.order_data)

        # Validate that the API call was made
        self.assertTrue(mocked.called)

        # Validate that the call was made with the given LoyaltyProgramOrder
        request_body = mocked.call_args[1]['body']
        self.assertEquals(request_body['customer_email'], self.order_data.customer_email)
        self.assertEquals(request_body['total_amount_cents'], self.order_data.total_amount_cents)
        self.assertEquals(request_body['currency_code'], self.order_data.currency_code)
        self.assertEquals(request_body['order_id'], self.order_data.order_id)
        self.assertEquals(request_body['status'], self.order_data.status)
        self.assertEquals(request_body['coupon_code'], self.order_data.coupon_code)
        self.assertEquals(request_body['ignore_ip_ua'], self.order_data.ignore_ip_ua)
        self.assertEquals(request_body['discount_amount_cents'], self.order_data.discount_amount_cents)
        self.assertEquals(request_body['items'][0]['name'], self.order_data.items[0]['name'])
        self.assertEquals(request_body['items'][0]['price_cents'], self.order_data.items[0]['price_cents'])
        self.assertEquals(request_body['items'][0]['vendor'], self.order_data.items[0]['vendor'])
        self.assertEquals(request_body['items'][0]['id'], self.order_data.items[0]['id'])
        self.assertEquals(request_body['items'][0]['type'], self.order_data.items[0]['type'])
        self.assertEquals(request_body['items'][0]['quantity'], self.order_data.items[0]['quantity'])
        self.assertEquals(request_body['items'][0]['collections'], self.order_data.items[0]['collections'])

    def test_will_raise_error_when_order_creation_fails(self):
        with mock.patch(
                'libs.api_request.make_logged_api_request',
                _mock_create_loyalty_order_error_response_object,
        ):
            with self.assertRaises(CouldNotCreateYotpoOrderError):
                self.client.create_order(self.order_data)

    def test_create_yotpo_refund(self):
        with mock.patch(
            'libs.api_request.make_logged_api_request',
            side_effect=_mock_create_loyalty_refund_success_response_object,
        ) as mocked:
            self.client.create_refund(self.refund_data)

        # Validate that the API call was made
        self.assertTrue(mocked.called)

        # Validate that the call was made with the given LoyaltyProgramRefund
        request_body = mocked.call_args[1]['body']
        self.assertEquals(request_body['order_id'], self.refund_data.order_id)
        self.assertEquals(request_body['total_amount_cents'], self.refund_data.total_amount_cents)
        self.assertEquals(request_body['currency'], self.refund_data.currency)

    def test_will_raise_error_when_refund_creation_fails(self):
        with mock.patch(
            'libs.api_request.make_logged_api_request',
                _mock_create_loyalty_refund_error_response_object,
        ):
            with self.assertRaises(CouldNotCreateYotpoRefundError):
                self.client.create_refund(self.refund_data)
