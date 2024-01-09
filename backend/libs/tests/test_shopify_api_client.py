from django.test import TestCase

from apps.orders.tests.factories import OrderFactory
from libs.shopify_api_client import ShopifyAPIClient

from apps.addresses.tests.factories.location import LocationFactory
from apps.customers.tests.factories import CustomerFactory
from apps.discounts.tests.factories import CustomerDiscountFactory


class ShopifyAPIClientTestSuite(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = CustomerFactory()
        LocationFactory(customer=cls.customer)
        cls.order = OrderFactory(customer=cls.customer)

    def test_will_build_payload_from_order(self):
        client = ShopifyAPIClient()
        built_data = client._build_order_data(self.order)
        self.assertEqual(type(built_data), dict)

    def test_will_build_payload_with_applied_discount(self):
        client = ShopifyAPIClient()
        self.order.applied_discount = CustomerDiscountFactory()
        built_data = client._build_order_data(self.order)
        self.assertIn('discount_codes', built_data)
        self.assertEqual(type(built_data['discount_codes'][0]), dict)
