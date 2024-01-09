from unittest import mock

from rest_framework.test import APITestCase

from apps.addresses.tests.factories.location import LocationFactory
from apps.carts.tests.factories import CartLineItemFactory
from apps.customers.tests.factories import CustomerFactory, CustomerChildFactory
from apps.orders.tests.factories import ShippingRateFactory, OrderFactory
from apps.products.tests.factories import ProductFactory, ProductVariantFactory
from libs.tax_nexus.avalara import TaxProcessorClient
from libs.tax_nexus.avalara.client import CouldNotCalculateTaxForPurchaseError, CouldNotRecordTaxForPurchaseError, \
    CouldNotRecordTaxForRefundError


def _mock_payment_calculator(*args, **kwargs):
    class MockPaymentCalculator:
        def __init__(self):
            self.shipping_rate = None
            self.cart = None

        def from_cart(self, cart):
            return self

    return MockPaymentCalculator()

def _mock_valid_tax_address(*args, **kwargs):
    class MockValidTaxAddressResponse:
        def json(self):
            return {
                'validatedAddresses': [{
                    "addressType": "HighRiseOrBusinessComplex",
                    "line1": "12345 NW 85TH AVE APT 4012",
                    "line2": "",
                    "line3": "",
                    "city": "MIAMI",
                    "region": "FL",
                    "country": "US",
                    "postalCode": "33155-5357",
                    "latitude": 25.820329,
                    "longitude": -80.336132
                }],
                'coordinates': {
                    "latitude": 25.820329,
                    "longitude": -80.336132
                }
            }
    return MockValidTaxAddressResponse()


def _mock_invalid_tax_address(*args, **kwargs):
    class MockInvalidTaxAddress:
        def json(self):
            return {
                "validatedAddress":{
                "addressType": "HighRiseOrBusinessComplex",
                "line1": "12345 NW 85TH AVE APT 4012",
                "line2": "",
                "line3": "",
                "city": "MIAMI",
                "region": "FL",
                "country": "US",
                "postalCode": "33155-5357",
            },
            "messages": [
                {
                    "summary": "Address not geocoded.",
                    "details": "Address cannot be geocoded.",
                    "refersTo": "Address",
                    "severity": "Error",
                    "source": "Avalara.AvaTax.Common"
                },
                {
                    "summary": "The city could not be determined.",
                    "details": "The city could not be found or determined from postal code.",
                    "refersTo": "Address.City",
                    "severity": "Error",
                    "source": "Avalara.AvaTax.Common"
                }
            ]
            }
    return MockInvalidTaxAddress()


def _mock_invalid_address_tax_calculation_response(*args, **kwargs):
    class MockInvalidAddressTaxCalculationResponse:
        status_code = 400

        def json(self):
            return {
                'error': {
                    'message': 'Tax calculation cannot be determined. Zip is not valid for the state.',
                }
            }

    return MockInvalidAddressTaxCalculationResponse()


def _mock_valid_refund_response(*args, **kwargs):
    class MockValidaAddressTaxCalculationResponse:
        status_code = 201

        def json(self):
            return {
                'totalTax': -123.00
            }

    return MockValidaAddressTaxCalculationResponse()


def _mock_invalid_refund_response(*args, **kwargs):
    class MockInvalidRefundResponse:
        status_code: 404

        def json(self):
            return {
                'error': {
                    'message': 'Document not found.'
                }
            }

    return MockInvalidRefundResponse()


class TaxProcessorAPIClientTestSuite(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.customer = CustomerFactory()
        cls.address = LocationFactory(customer=cls.customer, city='Miami', zipcode=33179, street_address="GENERAL DELIVERYt")
        cls.taxClient = TaxProcessorClient().set_shipping_rate(ShippingRateFactory())
        cls.products = [
            ProductFactory(title='recipe-1'),
        ]
        for product in cls.products:
            cls.product_variant = ProductVariantFactory(product=product, sku_id='SKU-12')

    def setUp(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.customer_child = CustomerChildFactory(parent=self.customer)
        self.cart = self.customer_child.cart
        CartLineItemFactory(
            cart=self.cart,
            product=self.products[0],
            quantity=12,
            product_variant=self.product_variant
        )

    def test_can_verify_valid_address(self):
        with mock.patch(
            'libs.tax_nexus.avalara.AvalaraClient.resolve_address_post',
            side_effect=_mock_valid_tax_address,
        ):
            valid_address_response = self.taxClient.validate_tax_address(self.address)

        self.assertEqual(valid_address_response, {
            'valid_address': True,
            'messages': []
        })

    def test_receive_correct_payload_for_invalid_address(self):
        with mock.patch(
            'libs.tax_nexus.avalara.AvalaraClient.resolve_address_post',
            side_effect=_mock_invalid_tax_address,
        ):
            invalid_address_response = self.taxClient.validate_tax_address(self.address)

        self.assertEqual(invalid_address_response, {
            'valid_address': False,
            'messages': [
                'Address not geocoded.', 'The city could not be determined.'
            ]
        })

    def test_can_calculate_tax_with_valid_address(self):
        def _mock_calculation(*args):
            return {
                "totalTax": 0.78
            }

        with mock.patch(
            'libs.tax_nexus.avalara.client.TaxProcessorClient._create_sales_document',
            side_effect=_mock_calculation,
        ):
            response = self.taxClient.calculate_tax(self.cart)

        self.assertEqual(response, {
            'total_tax': 0.78,
            'tax_rate': 0,
        })

    def test_cannot_calculate_tax_with_invalid_address(self):
        def _mock_error(*args, **kwargs):
            return {
                'error': 'mock ERROR'
            }
        with mock.patch(
            'libs.tax_nexus.avalara.client.TaxProcessorClient._create_sales_document',
            side_effect=_mock_error,
        ):
            with self.assertRaises(CouldNotCalculateTaxForPurchaseError):
                self.taxClient.calculate_tax(self.cart)

    def test_create_tax_record_with_valid_data(self):
        def _mock_calulation(*args):
            return {
                "total_tax": 0.78
            }

        with mock.patch(
            'libs.tax_nexus.avalara.client.TaxProcessorClient.charge',
            side_effect=_mock_calulation,
        ):
            response = self.taxClient.charge(self.cart, 'fake-order-id')
        self.assertEquals(response.get('total_tax'),  0.78)

    def test_cannot_create_tax_record_with_invalid_data(self):
        def _mock_error(*args, **kwargs):
            return {
                'error': 'mock ERROR'
            }
        with mock.patch(
            'libs.tax_nexus.avalara.client.TaxProcessorClient._create_sales_document',
            side_effect=_mock_error,
        ):
            with self.assertRaises(CouldNotRecordTaxForPurchaseError):
                self.taxClient.charge(self.cart, OrderFactory().id)

    def test_can_refund_created_tax_transaction_with_right_data(self):
        with mock.patch(
            'libs.tax_nexus.avalara.AvalaraClient.refund_transaction',
            side_effect=_mock_valid_refund_response
        ):
            response = self.taxClient.refund('valid-order-id')

        self.assertEqual(response, {
                'totalTax': -123.00
        })

    def test_can_cannot_refund_tax_transaction_with_invalid_order_id(self):
        with mock.patch(
            'libs.tax_nexus.avalara.AvalaraClient.refund_transaction',
            side_effect=_mock_invalid_refund_response
        ):
            with self.assertRaises(CouldNotRecordTaxForRefundError):
                self.taxClient.refund('invalid_order_id')








