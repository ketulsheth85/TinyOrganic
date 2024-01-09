from unittest import mock

from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from apps.carts.tests.factories import CartFactory, CartLineItemFactory
from apps.customers.tests.factories import CustomerChildFactory, CustomerFactory, CustomerSubscriptionFactory
from apps.products.tasks import (
    deactivate_products_set_to_deactivate_today,
    replace_product_in_cart_line_items_for_active_subscribers,
    _replace_cart_line_item,
)
from apps.products.tests.factories import ProductFactory, ProductVariantFactory

#
# class ProductsTasksTestSuite(TestCase):
#     def test_will_deactivate_products_with_a_deactivation_date_set(self):
#         with freeze_time(time_to_freeze=timezone.now()):
#             product = ProductFactory(title='deactivated-recipe', deactivation_date=timezone.now().date(), is_active=True)
#             deactivate_products_set_to_deactivate_today()
#             product.refresh_from_db()
#             self.assertFalse(product.is_active)
#
#     def test_will_create_a_new_line_item_with_existing_product_when_only_1_cart_line_item_exists(self):
#         product1 = ProductFactory(title='Apple Oatmeal', product_type='recipe', is_active=True)
#         product_variant112 = ProductVariantFactory(product=product1, sku_id='APPLEOAT-12')
#         ProductVariantFactory(product=product1, sku_id='APPLEOAT-24')
#         product2 = ProductFactory(title='Bananaz', product_type='recipe', is_active=True)
#         ProductVariantFactory(product=product2, sku_id='BANANAZ-12')
#         ProductVariantFactory(product=product2, sku_id='BANANAZ-24')
#
#         customer = CustomerFactory()
#         child = CustomerChildFactory(parent=customer)
#         CustomerSubscriptionFactory(customer=customer, customer_child=child, is_active=True, number_of_servings=12)
#         cart = CartFactory(customer_child=child, customer=customer)
#         CartLineItemFactory(
#             product=product1,
#             quantity=12,
#             product_variant=product_variant112,
#             cart=cart,
#         )
#         product1.is_active = False
#         product1.save()
#         _replace_cart_line_item(cart.id, product1.id)
#         cart.refresh_from_db()
#
#         self.assertEqual(cart.line_items.first().product, product2)
#
#     def test_will_replace_with_another_product_when_multiple_products_exist_in_cart_line_items(self):
#         product1 = ProductFactory(title='Apple Oatmeal')
#         ProductVariantFactory(product=product1, sku_id='APPLEOAT-12')
#         product_variant124 = ProductVariantFactory(product=product1, sku_id='APPLEOAT-24')
#         product2 = ProductFactory(title='Bananaz')
#         ProductVariantFactory(product=product2, sku_id='BANANAZ-12')
#         product_variant224 = ProductVariantFactory(product=product2, sku_id='BANANAZ-24')
#
#         customer = CustomerFactory()
#         child = CustomerChildFactory(parent=customer)
#         CustomerSubscriptionFactory(customer=customer, customer_child=child, is_active=True, number_of_servings=24)
#         cart = CartFactory(customer_child=child, customer=customer)
#         CartLineItemFactory(
#             product=product1,
#             quantity=12,
#             product_variant=product_variant124,
#             cart=cart,
#         )
#         CartLineItemFactory(
#             product=product2,
#             quantity=12,
#             product_variant=product_variant224,
#             cart=cart,
#         )
#         product1.is_active = False
#         product1.save()
#
#         _replace_cart_line_item(cart.id, product1.id)
#         cart.refresh_from_db()
#         self.assertTrue(cart.line_items.filter(product=product2).first().quantity, 24)
#
#     def test_will_invoke_task_to_replace_the_cart_with_line_items(self):
#         product1 = ProductFactory(title='Apple Oatmeal')
#         ProductVariantFactory(product=product1, sku_id='APPLEOAT-12')
#         product_variant124 = ProductVariantFactory(product=product1, sku_id='APPLEOAT-24')
#         product2 = ProductFactory(title='Bananaz')
#         ProductVariantFactory(product=product2, sku_id='BANANAZ-12')
#         product_variant224 = ProductVariantFactory(product=product2, sku_id='BANANAZ-24')
#
#         customer = CustomerFactory()
#         child = CustomerChildFactory(parent=customer)
#         CustomerSubscriptionFactory(customer=customer, customer_child=child, is_active=True, number_of_servings=24)
#         cart = CartFactory(customer_child=child, customer=customer)
#         CartLineItemFactory(
#             product=product1,
#             quantity=12,
#             product_variant=product_variant124,
#             cart=cart,
#         )
#         CartLineItemFactory(
#             product=product2,
#             quantity=12,
#             product_variant=product_variant224,
#             cart=cart,
#         )
#         with mock.patch('apps.products.tasks._replace_cart_line_item.delay') as mocked:
#             replace_product_in_cart_line_items_for_active_subscribers(product1.id)
#
#         self.assertTrue(mocked.called)
