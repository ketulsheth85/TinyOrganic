import random
import uuid
from decimal import Decimal
from unittest import mock

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.addresses.tests.factories.location import LocationFactory
from apps.billing.tests.factories.payment_method import PaymentMethodFactory
from apps.carts.tests.factories import CartFactory, CartLineItemFactory
from apps.customers.tests.factories import CustomerFactory, CustomerChildFactory, CustomerSubscriptionFactory
from apps.discounts.libs import DiscountRuleTypeEnum
from apps.discounts.tests.factories.rule import RuleFactory
from apps.orders.libs import CannotBuildOrderError, OrderPaymentStatusEnum
from apps.discounts.tests.factories import DiscountFactory
from apps.orders.tests.factories import OrderFactory, ShippingRateFactory
from apps.products.tests.factories import ProductFactory


def _mock_charge(*args, **kwargs):
    class MockProcessedCharge:
        id = f'{uuid.uuid4()}'
        status = 'succeeded'
        amount = 1000

    return MockProcessedCharge()


def _mock_calculate_tax(*args, **kwargs):
    return {
        'status_code': 200,
        'error': '',
        'total_tax': Decimal(0.0)
    }


@mock.patch('libs.tax_nexus.avalara.client.TaxProcessorClient.calculate_tax', side_effect=_mock_calculate_tax)
@mock.patch('apps.orders.tasks.sync_order_to_tax_client', side_effect=lambda: None)
@mock.patch('apps.orders.tasks.sync_refund_to_tax_client', side_effect=lambda: None)
class OrderViewSetAPITestSuite(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.random_customer = CustomerFactory()
        cls.payment_method = PaymentMethodFactory(customer=cls.random_customer)
        cls.order = OrderFactory(payment_method=cls.payment_method)

    def setUp(self) -> None:
        ShippingRateFactory(is_default=True)
        LocationFactory(customer=self.random_customer, )

    def test_cannot_fetch_another_customers_orders(self, *args):
        url = reverse('order-list')
        response = self.client.get(f'{url}?customer={self.random_customer.id}')
        self.assertEqual([], response.json())

    def test_can_fetch_orders_placed_by_customer(self, *args):
        url = reverse('order-list')
        response = self.client.get(f'{url}?customer={self.order.customer.id}')
        self.assertNotEqual([], response.json())

    def test_cannot_create_order_without_customer_id(self, *args):
        url = reverse('order-list')
        cart = CartFactory(customer=self.random_customer, customer_child__parent=self.random_customer)
        CartLineItemFactory(quantity=12, cart=cart)

        post_data = {
            'carts': [f'{cart.id}'],
        }
        with self.assertRaises(CannotBuildOrderError):
            self.client.post(url, post_data, format='json')

    def test_can_create_charged_order(self, *args):
        url = reverse('order-list')
        PaymentMethodFactory(customer=self.random_customer, is_valid=True, setup_for_future_charges=True)
        cart = CartFactory(customer=self.random_customer, customer_child__parent=self.random_customer)
        CartLineItemFactory(quantity=12, cart=cart)

        post_data = {
            'customer': f'{self.random_customer.id}',
            'carts': [f'{cart.id}'],
        }
        with mock.patch(
            'libs.payment_processors.stripe.client.PaymentProcessorClient.charge',
            side_effect=_mock_charge,
        ):
            response = self.client.post(url, post_data, format='json')
            self.assertEqual(response.json()[0]['paymentStatus'], 'paid')

    def test_creating_charged_order_will_remove_addons_from_cart(self, *args):
        url = reverse('order-list')
        PaymentMethodFactory(customer=self.random_customer, is_valid=True, setup_for_future_charges=True)
        recipe_product = ProductFactory(product_type='recipe')
        addon_product = ProductFactory(product_type='add_on', is_recurring=False)
        cart = CartFactory(customer=self.random_customer, customer_child__parent=self.random_customer)
        CartLineItemFactory(quantity=12, cart=cart, product=recipe_product)
        CartLineItemFactory(quantity=10, cart=cart, product=addon_product)
        post_data = {
            'carts': [f'{cart.id}'],
            'customer': f'{self.random_customer.id}',
        }
        with mock.patch(
            'libs.payment_processors.stripe.client.PaymentProcessorClient.charge',
            side_effect=_mock_charge,
        ):
            response = self.client.post(url, post_data, format='json')
            self.assertEqual(response.json()[0]['paymentStatus'], 'paid')
        cart_line_items = cart.line_items.filter()
        self.assertEqual(len(cart_line_items), 1)
        self.assertEqual(cart_line_items[0].product.product_type, 'recipe')

    def test_will_not_create_order_without_complete_shipping_address(self, *args):
        url = reverse('order-list')
        PaymentMethodFactory(customer=self.random_customer, is_valid=True, setup_for_future_charges=True)
        recipe_product = ProductFactory(product_type='recipe')
        addon_product = ProductFactory(product_type='add_on', is_recurring=False)
        cart = CartFactory(customer=self.random_customer, customer_child__parent=self.random_customer)
        CartLineItemFactory(quantity=12, cart=cart, product=recipe_product)
        CartLineItemFactory(quantity=10, cart=cart, product=addon_product)
        shipping_address = self.random_customer.addresses.first()
        shipping_address.state = None
        shipping_address.save()
        post_data = {
            'carts': [f'{cart.id}'],
            'customer': f'{self.random_customer.id}',
        }

        with self.assertRaises(CannotBuildOrderError):
            self.client.post(url, post_data, format='json')

    def test_will_not_create_order_for_deleted_child(self, *args):
        customer_child = CustomerChildFactory(parent=self.random_customer)
        CustomerSubscriptionFactory(customer=self.random_customer, customer_child=customer_child)
        cart = CartFactory(customer_child=customer_child, customer=self.random_customer)
        CartLineItemFactory(quantity=12, cart=cart)
        customer_child.delete()

        post_data = {
            'customer': f'{self.random_customer.id}',
            'carts': [f'{cart.id}'],
        }
        url = reverse('order-list')
        with mock.patch(
            'libs.payment_processors.stripe.client.PaymentProcessorClient.charge',
            side_effect=_mock_charge,
        ):
            response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.json(), [])

    def test_can_access_order_line_items_for_orders(self, *args):
        url = reverse('order-list')
        PaymentMethodFactory(customer=self.random_customer, is_valid=True, setup_for_future_charges=True)
        cart = CartFactory(customer=self.random_customer, customer_child__parent=self.random_customer)
        CartLineItemFactory(quantity=12, cart=cart)

        post_data = {
            'customer': f'{self.random_customer.id}',
            'carts': [f'{cart.id}'],
        }

        with mock.patch(
                'libs.payment_processors.stripe.client.PaymentProcessorClient.charge',
                side_effect=_mock_charge,
        ):
            response = self.client.post(url, post_data, format='json')
            self.assertTrue(len(response.json()[0]['orderLineItems']))

    def test_order_summary_can_be_retrieved_from_customer_without_discount_code(self, *args):
        url = reverse('order-summary')
        cart = CartFactory(customer=self.random_customer, customer_child__parent=self.random_customer)
        CartLineItemFactory(quantity=12, cart=cart)
        url = f'{url}?customer={self.random_customer.id}'
        response = self.client.get(url)
        self.assertEqual(response.json()['discounts'], Decimal('0'))

    def test_order_summary_can_be_retrieved_from_customer_with_discount_code(self, *args):
        url = reverse('order-summary')
        cart = CartFactory(customer=self.random_customer, customer_child__parent=self.random_customer)
        CartLineItemFactory(quantity=12, cart=cart)
        discount = DiscountFactory(discount_type='percentage', is_active=True)
        RuleFactory(
            discount=discount,
            type=DiscountRuleTypeEnum.minimum_price,
            minimum_cart_amount=Decimal('0'),
            is_active=True,
        )
        url = f'{url}?customer={self.random_customer.id}&discount={discount.codename}'
        response = self.client.get(url)
        value = Decimal('0')
        self.assertGreater(response.json()['discounts'], value)

    def test_can_retrieve_latest_customer_order_when_customer_has_one_order(self, *args):
        customer = CustomerFactory()
        self.client.force_login(customer)
        customer_child = CustomerChildFactory(parent=customer)
        expected_order = OrderFactory(
            customer=customer,
            customer_child=customer_child,
            payment_method=self.payment_method,
            payment_status=OrderPaymentStatusEnum.paid,
        )
        url = reverse('order-latest')

        response = self.client.get(
            f'{url}?customer={customer.id}&customer_child={customer_child.id}'
        )
        latest_order = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(latest_order.get('id'), str(expected_order.id))

    def test_can_retrieve_latest_customer_order_when_customer_has_multiple_orders(self, *args):
        customer = CustomerFactory()
        self.client.force_login(customer)
        customer_child = CustomerChildFactory(parent=customer)
        
        OrderFactory(
            customer=customer,
            customer_child=customer_child,
            payment_method=self.payment_method,
            payment_status=OrderPaymentStatusEnum.paid,
        )
        expected_order = OrderFactory(
            customer=customer,
            customer_child=customer_child,
            payment_method=self.payment_method,
            payment_status=OrderPaymentStatusEnum.paid,
        )
        url = reverse('order-latest')

        response = self.client.get(
            f'{url}?customer={customer.id}&customer_child={customer_child.id}'
        )
        latest_order = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(latest_order.get('id'), str(expected_order.id))         
        
    def test_can_retrieve_latest_customer_order_regardless_of_payment_status(self, *args):
        customer = CustomerFactory()
        self.client.force_login(customer)
        customer_child = CustomerChildFactory(parent=customer)
        
        OrderFactory(
            customer=customer,
            customer_child=customer_child,
            payment_method=self.payment_method,
            payment_status=OrderPaymentStatusEnum.refunded
        )
        
        for status in OrderPaymentStatusEnum:
            expected_order = OrderFactory(
                customer=customer,
                customer_child=customer_child,
                payment_method=self.payment_method,
                payment_status=status
            )
            url = reverse('order-latest')
            
            response = self.client.get(
                f'{url}?customer={customer.id}&customer_child={customer_child.id}'
            )
            
            latest_order = response.json()
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(latest_order.get('id'), str(expected_order.id))
    
    def test_can_retrieve_the_latest_order_after_updated_order_status(self, *args):
        customer = CustomerFactory()
        self.client.force_login(customer)
        customer_child = CustomerChildFactory(parent=customer)
        
        random_payment_method = random.choice(list(OrderPaymentStatusEnum))
        
        OrderFactory(
            customer=customer,
            customer_child=customer_child,
            payment_method=self.payment_method,
            payment_status=OrderPaymentStatusEnum.paid
        )
        updated_order = OrderFactory(
            customer=customer,
            customer_child=customer_child,
            payment_method=self.payment_method,
            payment_status=random_payment_method
        )
        
        url = reverse('order-latest')
        
        response = self.client.get(
            f'{url}?customer={customer.id}&customer_child={customer_child.id}'
        )
                
        order = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(order['id'], str(updated_order.id))
