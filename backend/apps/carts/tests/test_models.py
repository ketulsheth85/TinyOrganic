from django.test import TestCase

from apps.carts.tests.factories import CartFactory, CartLineItemFactory


class CartModelTestSuite(TestCase):
    def test_will_remove_non_recurring_items_from_cart(self):
        cart = CartFactory()
        CartLineItemFactory(cart=cart, product__is_recurring=False)
        cart.remove_onetime_line_items()
        self.assertIsNone(cart.line_items.first())

    def test_will_not_remove_recurring_items_from_cart(self):
        cart = CartFactory()
        CartLineItemFactory(cart=cart, product__is_recurring=True)
        cart.remove_onetime_line_items()
        self.assertIsNotNone(cart.line_items.first())
