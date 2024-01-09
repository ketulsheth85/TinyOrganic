from decimal import Decimal
from unittest import mock

from django.test import TestCase

from apps.addresses.tests.factories.location import LocationFactory
from apps.billing.tests.factories.payment_method import PaymentMethodFactory
from apps.carts.tests.factories import CartFactory
from apps.carts.tests.factories.cart_line_item import CartLineItemFactory
from apps.customers.tests.factories import (
    CustomerChildFactory,
    CustomerFactory,
    CustomerSubscriptionFactory,
)
from apps.discounts.libs import DiscountRuleTypeEnum
from apps.discounts.tests.factories.rule import RuleFactory
from apps.orders.libs import CannotBuildOrderError, OrderBuilder, PaymentCalculator
from apps.discounts.tests.factories import CustomerDiscountFactory, DiscountFactory
from apps.orders.tests.factories import ShippingRateFactory
from apps.products.tests.factories import ProductFactory, ProductVariantFactory


class OrderBuilderTestSuite(TestCase):
    def setUp(self) -> None:
        ShippingRateFactory()
        self.customer = CustomerFactory()
        self.child = CustomerChildFactory(parent=self.customer)
        self.payment_method = PaymentMethodFactory(customer=self.customer)
        self.cart = CartFactory(customer=self.customer, customer_child=self.child)
        self.subscription = CustomerSubscriptionFactory(customer=self.customer)
        discount = DiscountFactory(discount_type='percentage', is_active=True)
        self.percent_discount = CustomerDiscountFactory(customer=self.customer, discount=discount)
        fixed_discount = DiscountFactory(discount_type='fixed amount', is_active=True)
        self.fixed_customer = CustomerFactory()
        self.fixed_payment_method = PaymentMethodFactory(customer=self.customer)
        self.fixed_child = CustomerChildFactory(parent=self.fixed_customer)
        self.fixed_cart = CartFactory(customer=self.customer, customer_child=self.fixed_child)
        self.fixed_subscription = CustomerSubscriptionFactory(customer=self.customer)
        self.fixed_amount_discount = CustomerDiscountFactory(customer=self.fixed_customer, discount=fixed_discount)
        self.shipping_rate = ShippingRateFactory(is_default=True)

    def test_will_deduct_20_dollars_from_subtotal_when_number_of_servings_is_24(self):
        customer = CustomerFactory()
        address = LocationFactory(customer=customer)
        child = CustomerChildFactory(parent=self.customer)
        payment_method = PaymentMethodFactory(customer=customer)
        cart = CartFactory(customer=customer, customer_child=child)
        line_item = CartLineItemFactory(cart=cart, product_variant__price=4.69, quantity=24)
        subscription = CustomerSubscriptionFactory(number_of_servings=24, customer=customer, customer_child=child)
        builder = OrderBuilder()\
            .set_number_of_servings(subscription.number_of_servings)\
            .set_customer(customer)\
            .set_shipping_address(address)\
            .add_line_item(line_item)\
            .set_payment_method(payment_method)\
            .set_shipping_rate(self.shipping_rate)\
            .build()
        subtotal_amount_before_automatic_20_dollar_discount = Decimal(f'{4.69 * 24}')
        self.assertLess(builder.subtotal_amount, subtotal_amount_before_automatic_20_dollar_discount)

    def test_will_not_deduct_20_dollars_from_subtotal_when_number_of_servings_is_not_24(self):
        customer = CustomerFactory()
        address = LocationFactory(customer=customer)
        child = CustomerChildFactory(parent=self.customer)
        payment_method = PaymentMethodFactory(customer=customer)
        cart = CartFactory(customer=customer, customer_child=child)
        line_item = CartLineItemFactory(cart=cart, product_variant__price=5.49, quantity=12)
        subscription = CustomerSubscriptionFactory(number_of_servings=12, customer=customer, customer_child=child)

        builder = OrderBuilder() \
            .set_number_of_servings(subscription.number_of_servings) \
            .set_customer(customer) \
            .add_line_item(line_item)\
            .set_shipping_address(address)\
            .set_shipping_rate(self.shipping_rate)\
            .set_payment_method(payment_method)\
            .build()
        subtotal_amount_before_automatic_20_dollar_discount = Decimal(f'{5.49 * 12}')
        self.assertEquals(builder.order.subtotal_amount, subtotal_amount_before_automatic_20_dollar_discount)

    def test_will_raise_error_when_is_not_supplied_a_customer(self):
        with self.assertRaises(CannotBuildOrderError):
            OrderBuilder().build()

    def test_will_raise_error_when_is_not_supplied_a_number_of_servings(self):
        with self.assertRaises(CannotBuildOrderError):
            OrderBuilder().set_customer(self.customer).build()

    def test_will_raise_error_if_order_creation_step_fails(self):
        def _mock_create_order_fail(*args, **kwargs):
            raise Exception('Something Happened')

        with mock.patch('apps.orders.libs.OrderBuilder._create_order', side_effects=_mock_create_order_fail):
            with self.assertRaises(CannotBuildOrderError):
                product = ProductFactory()
                line_item = CartLineItemFactory(
                    product=product,
                    cart=self.cart,
                    cart__customer_child=self.child,
                    cart__customer=self.customer
                )
                OrderBuilder()\
                    .set_customer(self.customer)\
                    .set_number_of_servings(12)\
                    .add_line_items([line_item, ])\
                    .build()

    def test_will_apply_one_percentage_discount_to_amount_total(self):
        CartLineItemFactory(cart=self.cart, quantity=12)
        calculator = PaymentCalculator.from_cart(self.cart)
        subtotal_before_discount = Decimal('5.49') * 12
        self.assertLess(calculator.amount_total, subtotal_before_discount)

    def test_will_apply_one_fixed_amount_discount_to_amount_total(self):
        calculator = PaymentCalculator.from_cart(self.cart)
        amount_before_applied_discount = Decimal('5.49') * 12

        calculated_amount_total = calculator.amount_total
        self.assertLess(calculated_amount_total, amount_before_applied_discount)
