from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.products.tests.factories.product import ProductFactory

#
# class ProductViewSetTestCase(APITestCase):
#     def test_can_fetch_products(self):
#         product_one = ProductFactory()
#         product_two = ProductFactory()
#         url = reverse('product-list')
#         response = self.client.get(url)
#         product_list = response.json()
#
#         count = (len(list(filter(
#             lambda p: p.get('id') == str(product_one.id) or p.get('id') == str(product_two.id),
#             product_list))
#         ))
#
#         self.assertEqual(count, 2)
