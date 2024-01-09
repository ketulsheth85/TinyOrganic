from unittest import mock

from django.test import TestCase

from apps.products.tests.factories import ProductFactory

#
# class ProductModelTestSuite(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.product = ProductFactory(is_active=True)
#
#     def test_will_invoke_method_to_replace_cart_line_items_with_deactivated_product(self):
#         with mock.patch(
#             'apps.products.models.product.Product._replace_cart_line_items_containing_product'
#         ) as mocked:
#             with self.captureOnCommitCallbacks(execute=True):
#                 self.product.is_active = False
#                 self.product.save()
#
#             self.assertTrue(mocked.called)
