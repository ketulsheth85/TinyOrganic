from decimal import Decimal

from django.test import TestCase

from apps.carts.tests.factories import CartFactory, CartLineItemFactory
from apps.customers.tests.factories import CustomerChildFactory, CustomerFactory
from apps.discounts.libs import DiscountRuleTypeEnum, DiscountBuilder, CannotCreateDiscountForCustomerError
from apps.discounts.tests.factories import DiscountFactory
from apps.discounts.tests.factories.rule import RuleFactory
from apps.orders.tests.factories import OrderFactory
from apps.products.tests.factories import ProductFactory, ProductVariantFactory


class DiscountBuilderTestSuite(TestCase):
    def setUp(self) -> None:
        self.customer = CustomerFactory()
        self.customer_child = CustomerChildFactory(parent=self.customer)
        self.cart = CartFactory(customer=self.customer, customer_child=self.customer_child)
        self.product = ProductFactory(title='apple oats')
        self.product12 = ProductVariantFactory(product=self.product, sku_id='OAT-12')
        self.product24 = ProductVariantFactory(product=self.product, sku_id='OAT-24')
        self.discount = DiscountFactory()

    def test_will_create_customer_discount_when_customer_child_has_met_minimum_cart_amount_rule(self):
        RuleFactory(
            discount=self.discount,
            type=DiscountRuleTypeEnum.minimum_price,
            minimum_cart_amount=Decimal('10.00'),
            is_active=True,
        )
        CartLineItemFactory(
            product=self.product,
            product_variant=self.product12,
            cart=self.cart,
            quantity=12,
        )
        builder = DiscountBuilder()\
            .set_discount(self.discount)\
            .add_cart(self.cart)\
            .build()
        self.assertIsNotNone(builder.customer_discounts)

    def test_will_raise_error_when_customer_does_not_meet_cart_minimum_amount_rule(self):
        with self.assertRaises(CannotCreateDiscountForCustomerError):
            RuleFactory(
                discount=self.discount,
                type=DiscountRuleTypeEnum.minimum_price,
                minimum_cart_amount=Decimal('100000.00'),
                is_active=True,
            )
            CartLineItemFactory(
                product=self.product,
                product_variant=self.product12,
                cart=self.cart,
                quantity=12,
            )
            DiscountBuilder() \
                .set_discount(self.discount) \
                .add_cart(self.cart) \
                .build()

    def test_will_raise_error_when_no_discount_is_not_applied_to_any_cart(self):
        with self.assertRaises(CannotCreateDiscountForCustomerError):
            fixed_discount = DiscountFactory(
                discount_type='percentage discount',
                is_active=True
            )
            RuleFactory(
                discount=fixed_discount,
                type=DiscountRuleTypeEnum.minimum_price,
                minimum_cart_amount=Decimal('100000.00'),
                is_active=True,
            )
            customer = CustomerFactory()
            discount_builder = DiscountBuilder() \
                .set_discount(fixed_discount)
            for i in range(3):
                customer_child = CustomerChildFactory(parent=customer)
                cart = CartFactory(customer=customer, customer_child=customer_child)
                discount_builder.add_cart(cart)
                CartLineItemFactory(
                    product=self.product,
                    product_variant=self.product12,
                    cart=cart,
                    quantity=12,
                )

            discount_builder.build()

    def test_will_create_customer_discount_when_customer_meets_the_cart_line_item_rules(self):
        RuleFactory(
            discount=self.discount,
            type=DiscountRuleTypeEnum.product,
            apply_to_products=[self.product],
            is_active=True
        )
        CartLineItemFactory(
            product=self.product,
            product_variant=self.product12,
            cart=self.cart,
            quantity=12,
        )
        builder = DiscountBuilder() \
            .set_discount(self.discount) \
            .add_cart(self.cart) \
            .build()
        self.assertIsNotNone(builder.customer_discounts)

    def test_will_raise_error_when_customer_does_not_meet_the_cart_line_item_rules(self):
        RuleFactory(
            discount=self.discount,
            type=DiscountRuleTypeEnum.product,
            apply_to_products=[ProductFactory()],
            is_active=True,
        )
        CartLineItemFactory(
            product=self.product,
            product_variant=self.product12,
            cart=self.cart,
            quantity=12,
        )
        with self.assertRaises(CannotCreateDiscountForCustomerError):
            DiscountBuilder() \
                .set_discount(self.discount) \
                .add_cart(self.cart) \
                .build()

    def test_will_create_customer_discount_when_customer_is_in_the_customer_set_list_in_a_rule(self):
        RuleFactory(
            discount=self.discount,
            type=DiscountRuleTypeEnum.customer_set,
            apply_to_customers=[self.customer],
            is_active=True,
        )
        CartLineItemFactory(
            product=self.product,
            product_variant=self.product12,
            cart=self.cart,
            quantity=12,
        )
        builder = DiscountBuilder() \
            .set_discount(self.discount) \
            .add_cart(self.cart) \
            .build()
        self.assertIsNotNone(builder.customer_discounts)

    def test_will_raise_error_when_customer_is_not_in_the_customer_set_list_in_rule(self):
        RuleFactory(
            discount=self.discount,
            type=DiscountRuleTypeEnum.customer_set,
            apply_to_customers=[CustomerFactory()],
            is_active=True,
        )
        CartLineItemFactory(
            product=self.product,
            product_variant=self.product12,
            cart=self.cart,
            quantity=12,
        )
        with self.assertRaises(CannotCreateDiscountForCustomerError):
            DiscountBuilder() \
                .set_discount(self.discount) \
                .add_cart(self.cart) \
                .build()

    def test_will_create_customer_discount_for_carts_that_can_meet_the_combined_ruleset(self):
        RuleFactory(
            discount=self.discount,
            type=DiscountRuleTypeEnum.product,
            apply_to_products=[self.product],
            is_active=True,
        )
        RuleFactory(
            discount=self.discount,
            type=DiscountRuleTypeEnum.minimum_price,
            minimum_cart_amount=Decimal('10.00'),
            is_active=True,
        )
        CartLineItemFactory(
            product=self.product,
            product_variant=self.product12,
            cart=self.cart,
            quantity=12,
        )
        builder = DiscountBuilder() \
            .set_discount(self.discount) \
            .add_cart(self.cart) \
            .build()
        self.assertIsNotNone(builder.customer_discounts)

    def test_will_raise_error_when_customer_does_meet_all_conditions_in_ruleset(self):
        RuleFactory(
            discount=self.discount,
            type=DiscountRuleTypeEnum.product,
            apply_to_products=[ProductFactory()],
            is_active=True,
        )
        RuleFactory(
            discount=self.discount,
            type=DiscountRuleTypeEnum.minimum_price,
            minimum_cart_amount=Decimal('10.00'),
            is_active=True,
        )
        CartLineItemFactory(
            product=self.product,
            product_variant=self.product12,
            cart=self.cart,
            quantity=12,
        )
        with self.assertRaises(CannotCreateDiscountForCustomerError):
            DiscountBuilder() \
                .set_discount(self.discount) \
                .add_cart(self.cart) \
                .build()

    def test_will_provide_discount_to_1st_time_subscriber(self):
        RuleFactory(
            discount=self.discount,
            type=DiscountRuleTypeEnum.nth_time_subscribers,
            nth_time_subscriber=1,
            is_active=True,
        )
        CartLineItemFactory(
            product=self.product,
            product_variant=self.product12,
            cart=self.cart,
            quantity=12,
        )
        builder = DiscountBuilder() \
            .set_discount(self.discount) \
            .add_cart(self.cart) \
            .build()
        self.assertIsNotNone(builder.customer_discounts)

    def test_will_raise_error_to_recurring_subscriber(self):
        OrderFactory(customer=self.customer, customer_child=self.customer_child)
        RuleFactory(
            discount=self.discount,
            type=DiscountRuleTypeEnum.nth_time_subscribers,
            nth_time_subscriber=1,
            is_active=True,
        )
        CartLineItemFactory(
            product=self.product,
            product_variant=self.product12,
            cart=self.cart,
            quantity=12,
        )
        with self.assertRaises(CannotCreateDiscountForCustomerError):
            DiscountBuilder() \
                .set_discount(self.discount) \
                .add_cart(self.cart) \
                .build()

    def test_will_only_apply_fixed_discounts_to_first_child(self):
        fixed_discount = DiscountFactory(
            discount_type='fixed amount',
            is_active=True
        )
        customer = CustomerFactory()
        discount_builder = DiscountBuilder()\
            .set_discount(fixed_discount)
        for i in range(3):
            customer_child = CustomerChildFactory(parent=customer)
            cart = CartFactory(customer=customer, customer_child=customer_child)
            discount_builder.add_cart(cart)
            CartLineItemFactory(
                product=self.product,
                product_variant=self.product12,
                cart=cart,
                quantity=12,
            )

        discount_builder.build()

        self.assertEqual(len(discount_builder.customer_discounts), 1)

    def test_will_raise_error_when_user_tries_to_use_their_own_discount(self):
        customer = CustomerFactory()
        customer_child = CustomerChildFactory(parent=customer)
        discount = DiscountFactory(referrer=customer, is_active=True)
        cart = CartFactory(customer=customer, customer_child=customer_child)
        CartLineItemFactory(
            product=self.product,
            product_variant=self.product12,
            cart=cart,
            quantity=12,
        )

        discount_builder = DiscountBuilder() \
            .set_discount(discount) \
            .add_cart(cart)

        with self.assertRaises(CannotCreateDiscountForCustomerError):
            discount_builder.build()

    def test_will_create_customer_discount_when_customer_uses_referral_discount(self):
        discount = DiscountFactory(referrer=CustomerFactory(), is_active=True)
        CartLineItemFactory(
            product=self.product,
            product_variant=self.product12,
            cart=self.cart,
            quantity=12,
        )
        builder = DiscountBuilder() \
            .set_discount(discount) \
            .add_cart(self.cart) \
            .build()
        self.assertIsNotNone(builder.customer_discounts)
