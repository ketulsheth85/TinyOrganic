from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.carts.tests.factories.cart_line_item import CartLineItemFactory
from apps.customers.tests.factories import (
    CustomerChildFactory,
    CustomerFactory,
    CustomerSubscriptionFactory,
)
from apps.products.tests.factories import ProductFactory, ProductVariantFactory


class CartAPITestSuite(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = CustomerFactory()
        cls.products = [
            ProductFactory(title='recipe-1'),
            ProductFactory(title='recipe-2'),
        ]
        for product in cls.products:
            ProductVariantFactory(product=product, sku_id='SKU-12')
            ProductVariantFactory(product=product, sku_id='SKU-24')

    def setUp(self) -> None:
        with self.captureOnCommitCallbacks(execute=True):
            self.customer_child = CustomerChildFactory(parent=self.customer)
        self.cart = self.customer_child.cart
        CustomerSubscriptionFactory(customer=self.customer, customer_child=self.customer_child, number_of_servings=12)

    def test_that_can_list_customer_carts(self):
        url = reverse('cart-list')
        response = self.client.get(f'{url}?customer={self.customer.id}')
        self.assertIsNotNone(response.json())

    def test_will_not_list_customer_carts(self):
        url = reverse('cart-list')
        response = self.client.get(url)
        self.assertEqual(len(response.json()), 0)

    def test_can_add_line_item_to_customer_cart(self):
        url = reverse('cart-detail', args=[f'{self.cart.id}'])
        patch_data = {
            'line_items': [
                {
                    'product': {'id': f'{self.products[0].id}', 'title': self.products[0].title},
                    'quantity': 1
                }
            ]
        }
        response = self.client.patch(f'{url}?customer={self.customer.id}', data=patch_data, format='json')
        self.assertEqual(response.json()['lineItems'][0]['product']['id'], f'{self.products[0].id}')

    def test_can_make_updates_to_existing_line_item_to_customer_cart(self):
        url = reverse('cart-detail', args=[f'{self.cart.id}'])
        line_item = CartLineItemFactory(cart=self.cart, product=self.products[0], quantity=1)

        patch_data = {
            'line_items': [
                {
                    'id': f'{line_item.product.id}',
                    'product': {
                        'id': str(self.products[0].id),
                        'title': self.products[0].title
                    }, 'quantity': 12
                }
            ]
        }
        response = self.client.patch(f'{url}?customer={self.customer.id}', data=patch_data, format='json')

        self.assertEqual(response.json()['lineItems'][0]['quantity'], 12)

    def test_can_remove_line_items_from_customer_cart(self):
        url = reverse('cart-detail', args=[f'{self.cart.id}'])
        CartLineItemFactory(cart=self.cart, product=self.products[0], quantity=1)
        patch_data = {
            'line_items': [
                {'id': f'{line_item.product.id}', 'product': {
                    'id': str(self.products[0].id),
                    'title': self.products[0].title
                }, 'quantity': 0}
                for line_item in self.cart.line_items.filter()
            ]
        }
        response = self.client.patch(f'{url}?customer={self.customer.id}', data=patch_data, format='json')
        self.assertEqual(len(response.json()['lineItems']), 0)
