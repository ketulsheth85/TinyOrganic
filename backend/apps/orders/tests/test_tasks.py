import uuid
from collections import namedtuple
from decimal import Decimal
from unittest import mock

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from backend.apps.discounts.tests.factories.discount import DiscountFactory
from factory.fuzzy import FuzzyInteger
from django.template import loader

from apps.addresses.tests.factories.location import LocationFactory
from apps.discounts.tests.factories import CustomerDiscountFactory
from apps.orders.libs import OrderPaymentStatusEnum
from apps.orders.models import Order
from apps.orders.tasks.recurring import (
    delete_pending_order,
    _charge_order,
    delete_pending_orders_for_non_subscribers,
)
from libs.payment_processors.exceptions import CouldNotChargeOrderError
from libs.shopify_api_client import CouldNotSyncRefundError

from apps.billing.tests.factories import PaymentMethodFactory
from apps.carts.tests.factories import CartFactory, CartLineItemFactory
from apps.customers.tests.factories import (
    CustomerChildFactory,
    CustomerFactory,
    CustomerSubscriptionFactory,
)
from apps.orders.tasks import (
    create_new_orders_for_active_subscribers,
    sync_order_to_shopify,
    sync_refunded_order_to_shopify,
    send_order_confirmation_email,
    sync_order_to_yotpo,
    sync_refund_to_yotpo,
)
from apps.orders.tests.factories import OrderFactory, OrderLineItemFactory
from apps.products.tests.factories import ProductFactory


def _mock_create_shopify_order(*args, **kwargs):
    class MockResponseObj:
        id = FuzzyInteger(low=1000, high=1000000).fuzz()
        order_number = FuzzyInteger(low=1000, high=1000000).fuzz()
    return MockResponseObj()


def _mock_get_shopify_customer(*args, **kwargs):
    class MockedResponseObj:
        id = FuzzyInteger(low=1000, high=1000000).fuzz()

    return MockedResponseObj


def _mock_create_loyalty_order_success_response_object(*args, **kwargs):
    class MockedResponseObj:
        status_code = 200

        def json(self):
            return {}

    return MockedResponseObj()


def _mock_create_loyalty_refund_success_response_object(*args, **kwargs):
    class MockedResponseObj:
        status_code = 200

        def json(self):
            return {}

    return MockedResponseObj()


def _mock_raise_refund_error(*args, **kwargs):
    raise CouldNotSyncRefundError


class MockedException(Exception):
    ...


def _mock_raise_error(*args, **kwargs):
    raise MockedException("MOCK")


class OrderSyncToShopifyTestSuite(TestCase):
    @classmethod
    def setUpTestData(cls):
        subscription = CustomerSubscriptionFactory()
        LocationFactory(customer=subscription.customer)
        cls.order = OrderFactory(customer=subscription.customer)

    def test_will_make_call_to_shopify_to_sync_order(self):
        self.order.payment_status = 'paid'
        self.order.synced_to_shopify = False
        self.order.order_number = None
        self.order.external_order_id = None
        self.order.payment_processor_charge_id = 'some-charge-id'
        self.order.save()

        with mock.patch(
            'apps.orders.tasks.order._create_shopify_customer',
            side_effect=_mock_get_shopify_customer,
        ):
            with mock.patch(
                'libs.shopify_api_client.ShopifyAPIClient.create_order',
                side_effect=_mock_create_shopify_order,
            ) as mocked:
                with mock.patch(
                    'libs.shopify_api_client.ShopifyAPIClient.create_transaction_for_order',
                    side_effect=lambda *args: True,
                ):
                    with mock.patch(
                            'apps.orders.models.order.Order.objects.get',
                            side_effect=lambda *args, **kwargs: self.order,
                    ):
                        sync_order_to_shopify(self.order.id)

        self.assertTrue(mocked.called)

    def test_will_set_the_shopify_order_id_in_the_database_after_syncing(self):
        self.order.payment_status = 'paid'
        self.order.synced_to_shopify = False
        self.order.order_number = None
        self.order.external_order_id = None
        self.order.payment_processor_charge_id = 'some-charge-id'
        self.order.save()
        with mock.patch(
            'apps.orders.tasks.order._create_shopify_customer',
            side_effect=_mock_get_shopify_customer,
        ):
            with mock.patch(
                'libs.shopify_api_client.ShopifyAPIClient.create_order',
                side_effect=_mock_create_shopify_order,
            ):
                with mock.patch(
                    'libs.shopify_api_client.ShopifyAPIClient.create_transaction_for_order',
                    side_effect=lambda *args: True,
                ):
                    sync_order_to_shopify(self.order.id)

        self.order.refresh_from_db()
        self.assertIsNotNone(self.order.external_order_id)

    def test_will_raise_an_exception_if_occurs_during_sync(self):
        self.order.payment_status = 'paid'
        self.order.synced_to_shopify = False
        self.order.order_number = None
        self.order.external_order_id = None
        self.order.payment_processor_charge_id = 'some-charge-id'
        self.order.save()
        with mock.patch(
            'apps.orders.tasks.order._create_shopify_customer',
            side_effect=_mock_get_shopify_customer,
        ):
            with mock.patch(
                'libs.shopify_api_client.ShopifyAPIClient.create_order',
                side_effect=_mock_raise_error,
            ):
                with mock.patch(
                        'apps.orders.models.order.Order.objects.get',
                        side_effect=lambda *args, **kwargs: self.order,
                ):
                    with self.assertRaises(MockedException):
                        sync_order_to_shopify(self.order.id)

    def test_will_raise_an_exception_if_occurs_during_refund_sync(self):
        with mock.patch(
            'libs.shopify_api_client.ShopifyAPIClient.refund_order',
            side_effect=_mock_raise_refund_error,
        ):
            with self.assertRaises(CouldNotSyncRefundError):
                sync_refunded_order_to_shopify(self.order.id)


class OrderTaskTestSuite(TestCase):
    def setUp(self) -> None:
        self.customer = CustomerFactory()
        self.child = CustomerChildFactory(parent=self.customer)
        self.cart = CartFactory(customer=self.customer,
                                customer_child=self.child)
        self.product = ProductFactory()
        CartLineItemFactory(cart=self.cart, product=self.product, quantity=12)
        self.payment_method = PaymentMethodFactory(
            customer=self.customer, is_valid=True, setup_for_future_charges=True)
        self.address = LocationFactory(customer=self.customer)
        self.subscription = CustomerSubscriptionFactory(
            customer=self.customer,
            customer_child=self.child,
            is_active=True,
            next_order_charge_date=timezone.now().date()
        )
        self.order = OrderFactory()

    def test_will_send_order_confirmation_email(self):
        def _mock_tax_calculation(*args):
            return {
                'tax_rate': Decimal('.0875'),
                'total_tax': Decimal('9.00'),
            }

        customer = CustomerFactory()
        child = CustomerChildFactory(parent=customer)
        CustomerSubscriptionFactory(
            customer=customer, customer_child=child, is_active=False)
        cart = CartFactory(customer=customer, customer_child=child)
        CartLineItemFactory.create_batch(2, cart=cart)
        payment_method = PaymentMethodFactory(
            customer=customer, is_valid=True, setup_for_future_charges=True)
        order = OrderFactory(
            payment_status=str(OrderPaymentStatusEnum.pending),
            customer_child=child,
            customer=customer,
            payment_method=payment_method,
        )

        with mock.patch('libs.email.send_email_message'):
            with mock.patch(
                'libs.tax_nexus.avalara.client.TaxProcessorClient.calculate_tax',
                side_effect=_mock_tax_calculation,
            ):
                send_order_confirmation_email(order.id)

        self.assertEqual(mail.outbox[0].subject,
                         '🌱 Your Tiny Organics Order is Confirmed!')

    @mock.patch('django.template.loader.render_to_string', side_effect=lambda *args, **kwargs: '')
    def test_will_send_order_confirmation_email_with_correct_fixed_discount_amount(self, mocked):
        def _mock_tax_calculation(*args):
            return {
                'tax_rate': Decimal('.0875'),
                'total_tax': Decimal('9.00'),
            }

        discount = DiscountFactory(discount_type='fixed amount')
        customer_discount = CustomerDiscountFactory(
            customer=self.customer,
            discount=discount,
        )

        order = OrderFactory(
            payment_status=str(OrderPaymentStatusEnum.pending),
            customer_child=self.child,
            customer=self.customer,
            payment_method=self.payment_method,
            applied_discount=customer_discount
        )

        with mock.patch('libs.email.send_email_message'):
            with mock.patch(
                'libs.tax_nexus.avalara.client.TaxProcessorClient.calculate_tax',
                side_effect=_mock_tax_calculation,
            ):
                send_order_confirmation_email(order.id)

        context = mocked.call_args[0][1]

        self.assertEquals(context.get(
            'applied_discount_amount'), discount.amount)


class OrderSyncToYotpoTestSuite(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.customer = CustomerFactory()

    def create_order(self):
        order = OrderFactory(customer=self.customer)
        order.line_items.add(OrderLineItemFactory())
        order.line_items.add(OrderLineItemFactory())
        return order

    def test_will_make_call_to_yotpo_to_sync_order(self):
        order = self.create_order()

        with mock.patch(
            'libs.yotpo_client.YotpoClient.create_order',
            side_effect=_mock_create_loyalty_order_success_response_object,
        ) as mocked:
            sync_order_to_yotpo(order.id)
            order.refresh_from_db()

        self.assertTrue(mocked.called)
        self.assertTrue(order.synced_to_yotpo)

    def test_will_not_make_call_to_yotpo_if_order_already_synced(self):
        order = self.create_order()
        order.synced_to_yotpo = True
        order.save()

        with mock.patch(
            'libs.yotpo_client.YotpoClient.create_order',
            side_effect=_mock_create_loyalty_order_success_response_object,
        ) as mocked:
            sync_order_to_yotpo(order.id)

        self.assertFalse(mocked.called)

    def test_will_make_call_to_yotpo_to_sync_refund(self):
        order = self.create_order()
        order.synced_to_yotpo = True
        order.save()

        with mock.patch(
            'libs.yotpo_client.YotpoClient.create_refund',
            side_effect=_mock_create_loyalty_refund_success_response_object,
        ) as mocked:
            sync_refund_to_yotpo(order.id)

        self.assertTrue(mocked.called)

    def test_will_not_make_call_to_yotpo_to_create_refund_if_order_not_synced(self):
        order = self.create_order()

        with mock.patch(
            'libs.yotpo_client.YotpoClient.create_refund',
            side_effect=_mock_create_loyalty_refund_success_response_object,
        ) as mocked:
            sync_refund_to_yotpo(order.id)

        self.assertFalse(mocked.called)
