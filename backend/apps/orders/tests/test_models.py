import uuid
from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from django_fsm import TransitionNotAllowed

from apps.billing.tests.factories import ChargeFactory
from apps.billing.tests.factories.payment_method import PaymentMethodFactory
from apps.customers.tests.factories import CustomerFactory, CustomerSubscriptionFactory
from apps.discounts.tests.factories import CustomerDiscountFactory
from apps.orders.libs import OrderPaymentStatusEnum
from apps.orders.tests.factories import OrderFactory
from apps.orders.tests.factories.order_line_item import OrderLineItemFactory
from apps.products.tests.factories import ProductFactory, ProductVariantFactory
from libs.shopify_api_client import CouldNotCancelOrderError


def _mock_payment_processor_transaction(*args, **kwargs):
    class ProcessedOrder:
        id = f'{uuid.uuid4()}'
        amount = Decimal('65.88')
        status = 'succeeded'
    return ProcessedOrder()


def _create_charge(*args, **kwargs):
    return ChargeFactory.build()


# class OrderModelTestSuite(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.customer = CustomerFactory()
#         cls.customer_subscription = CustomerSubscriptionFactory(is_active=True, customer=cls.customer)
#         cls.payment_method = PaymentMethodFactory(customer=cls.customer)
#         cls.unpaid_order = OrderFactory(customer=cls.customer, payment_method=cls.payment_method)
#
#     def test_can_fully_refund_order_when_in_paid_state(self, *args):
#         with mock.patch(
#             'libs.payment_processors.stripe.client.PaymentProcessorClient.charge',
#             side_effect=_mock_payment_processor_transaction,
#         ):
#             with mock.patch(
#                 'libs.shopify_api_client.ShopifyAPIClient.create_transaction_for_order',
#                 side_effect=lambda *args: True,
#             ):
#                 self.unpaid_order.charge()
#                 self.unpaid_order.save()
#
#         with mock.patch(
#             'libs.payment_processors.stripe.client.PaymentProcessorClient.refund',
#             side_effect=_mock_payment_processor_transaction,
#         ):
#             self.unpaid_order.refund()
#             self.unpaid_order.save()
#             self.assertIsNotNone(self.unpaid_order.refunded_at)
#             self.assertIsNotNone(self.unpaid_order.refunded_amount)
#
#     def test_will_mark_related_discount_code_as_redeemed_after_successfully_charging(self, *args):
#         customer_discount = CustomerDiscountFactory(customer=self.customer)
#         self.unpaid_order.applied_discount = customer_discount
#         self.unpaid_order.save()
#
#         with mock.patch(
#             'libs.payment_processors.stripe.client.PaymentProcessorClient.charge',
#             side_effect=_mock_payment_processor_transaction,
#         ):
#             with mock.patch(
#                 'libs.shopify_api_client.ShopifyAPIClient.create_transaction_for_order',
#                 side_effect=lambda *args: True,
#             ):
#                 with self.captureOnCommitCallbacks(execute=True):
#                     self.unpaid_order.charge()
#                     self.unpaid_order.save()
#
#         self.assertIsNotNone(self.unpaid_order.applied_discount.redeemed_at)
#
#     def test_will_create_task_to_send_order_to_shopify_and_avalara_once_order_is_successfully_charged(self, *args):
#         with self.captureOnCommitCallbacks(execute=True):
#             with mock.patch('apps.orders.models.order.Order._sync_paid_order_transaction') as mocked:
#                 with mock.patch(
#                     'apps.billing.models.payment_method.PaymentMethod._save_related_charge_to_db',
#                     side_effect=_create_charge,
#                 ):
#                     with mock.patch(
#                         'libs.payment_processors.stripe.client.PaymentProcessorClient.charge',
#                         side_effect=_mock_payment_processor_transaction,
#                     ):
#                         with mock.patch(
#                             'libs.shopify_api_client.ShopifyAPIClient.create_transaction_for_order',
#                             side_effect=lambda *args: True,
#                         ):
#                             self.unpaid_order.charge()
#                             self.unpaid_order.save()
#         self.assertTrue(mocked.called)
#
#     def test_will_create_task_to_refund_order_on_shopify_and_avalara_once_order_is_successfully_refunded(self, *args):
#         with mock.patch('apps.orders.models.order.Order._sync_paid_order_transaction'):
#             with mock.patch(
#                 'libs.payment_processors.stripe.client.PaymentProcessorClient.charge',
#                 side_effect=_mock_payment_processor_transaction,
#             ):
#                 with mock.patch(
#                     'libs.shopify_api_client.ShopifyAPIClient.create_transaction_for_order',
#                     side_effect=lambda *args: True,
#                 ):
#                     self.unpaid_order.charge()
#                     self.unpaid_order.save()
#
#         with self.captureOnCommitCallbacks(execute=True):
#             with mock.patch('apps.orders.models.order.Order._sync_refunded_order_transaction') as mocked:
#                 with mock.patch(
#                     'apps.billing.models.payment_method.PaymentMethod.refund',
#                     side_effect=_mock_payment_processor_transaction,
#                 ):
#                     self.unpaid_order.refund()
#                     self.unpaid_order.save()
#         self.assertTrue(mocked.called)
#
#     def test_will_not_create_task_to_send_order_to_shopify_when_order_charge_is_unsuccessful(self, *args):
#         def _mock_error(*args, **kwargs):
#             raise Exception("Something went wrong")
#
#         with mock.patch('apps.billing.models.payment_method.PaymentMethod.charge', side_effect=_mock_error) as mocked:
#             try:
#                 self.unpaid_order.charge()
#             except Exception:
#                 ...
#
#         self.assertEqual(self.unpaid_order.payment_status, OrderPaymentStatusEnum.pending)
#
#     def test_will_attempt_to_sync_a_cancelled_order_to_shopify_when_cancelling_order(self):
#         def _mock_raise_error():
#             raise CouldNotCancelOrderError(f'Could not cancel order {self.unpaid_order}')
#
#         with mock.patch('apps.orders.models.order.Order.cancel', side_effect=_mock_raise_error):
#             with self.assertRaises(CouldNotCancelOrderError):
#                 self.unpaid_order.cancel()
#
#     def test_will_not_allow_charging_an_order_if_cancelled(self):
#         def _mock_cancelled_order(*args):
#             class MockOrder:
#                 attributes = {'cancelled_at': timezone.now()}
#             return MockOrder()
#
#         with mock.patch('libs.shopify_api_client.ShopifyAPIClient.cancel_order', side_effect=_mock_cancelled_order):
#             self.unpaid_order.cancel()
#             self.unpaid_order.save()
#
#         with self.assertRaises(TransitionNotAllowed):
#             self.unpaid_order.charge()
#             self.unpaid_order.save()
#
#     def test_will_invoke_task_to_sync_partial_refund_to_shopify(self):
#         with mock.patch(
#             'libs.payment_processors.stripe.client.PaymentProcessorClient.charge',
#             side_effect=_mock_payment_processor_transaction,
#         ):
#             with mock.patch(
#                 'libs.shopify_api_client.ShopifyAPIClient.create_transaction_for_order',
#                 side_effect=lambda *args: True,
#             ):
#                 self.unpaid_order.charge()
#                 self.unpaid_order.save()
#
#         with self.captureOnCommitCallbacks(execute=True):
#             with mock.patch('apps.orders.models.order.Order._sync_partial_refunded_order_transaction') as mocked:
#                 with mock.patch(
#                     'libs.payment_processors.stripe.client.PaymentProcessorClient.refund',
#                     side_effect=_mock_payment_processor_transaction,
#                 ):
#                     self.unpaid_order.partially_refund()
#                     self.unpaid_order.save()
#
#         self.assertTrue(mocked.called)
#
#     def test_will_sync_order_charge_failed_event_to_analytics(self):
#         def _mock_error(*args, **kwargs):
#             raise Exception("Something went wrong")
#
#         self.unpaid_order.charge_attempts = 10
#         with mock.patch(
#             'libs.payment_processors.stripe.client.PaymentProcessorClient.charge',
#             side_effect=_mock_error,
#         ):
#             with self.captureOnCommitCallbacks(execute=True):
#                 with mock.patch('apps.orders.models.order.Order._sync_order_charge_failed_analytics_event') as mocked:
#                     try:
#                         self.unpaid_order.charge()
#                     except:
#                         ...
#                     finally:
#                         self.unpaid_order.save()
#
#             self.assertTrue(mocked.called)
#
#     def test_will_return_true_if_order_contains_24_products_of_type_recipe(self):
#         order = OrderFactory(customer=self.customer, payment_method=self.payment_method)
#         for i in range(24):
#             product = ProductFactory()
#             variant = ProductVariantFactory(product=product, sku_id=f'product{i}-24')
#             OrderLineItemFactory(order=order, product=product, product_variant=variant, quantity=1)
#
#         self.assertTrue((order.is_24_pack()))
#
#     def test_will_return_false_if_order_contains_less_than_24_products_of_type_recipe(self):
#         order = OrderFactory(customer=self.customer, payment_method=self.payment_method)
#         for i in range(12):
#             recipe_product = ProductFactory()
#             recipe_variant = ProductVariantFactory(product=recipe_product, sku_id=f'product{i}-12')
#             OrderLineItemFactory(order=order, product=recipe_product, product_variant=recipe_variant, quantity=1)
#
#             addon_product = ProductFactory(product_type="add-on")
#             addon_variant = ProductVariantFactory(product=addon_product)
#             OrderLineItemFactory(order=order, product=addon_product, product_variant=addon_variant, quantity=1)
#
#         self.assertFalse((order.is_24_pack()))
