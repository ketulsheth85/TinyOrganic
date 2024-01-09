from datetime import timedelta
from decimal import Decimal
from unittest import mock

from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from apps.carts.tests.factories import CartFactory
from apps.carts.tests.factories.cart_line_item import CartLineItemFactory
from apps.customers.tests.factories import (
    CustomerChildFactory,
    CustomerFactory,
    CustomerSubscriptionFactory,
)
# Create your tests here.
from apps.orders.tests.factories import OrderFactory
from apps.products.tests.factories import ProductFactory
from apps.recipes.tests.factories import IngredientFactory

from apps.customers.models.customer_subscription import SubscriptionStatusEnum


class CustomerModelTestCase(TestCase):
    def test_create_user_manager_creates_a_customer(self):
        Customer = apps.get_model('customers', 'Customer')
        customer = Customer.objects.create_user('foo@example.com', 'First', 'Last')
        self.assertIsInstance(customer, Customer)

    def test_create_user_will_raise_exception_if_missing_email(self):
        with self.assertRaises(ValueError):
            Customer = apps.get_model('customers', 'Customer')
            Customer.objects.create_user('', 'First', 'Last')

    def test_create_customer_has_full_name_property_which_returns_customer_full_name(self):
        Customer = apps.get_model('customers', 'Customer')
        customer = Customer.objects.create_user('foo@example.com', 'First', 'Last')
        self.assertEquals(customer.full_name, 'First Last')

    def test_create_superuser_creates_a_staff_user(self):
        Customer = apps.get_model('customers', 'Customer')
        customer = Customer.objects.create_superuser('foo@example.com', 'First', 'Last', 'mypass')
        self.assertTrue(customer.is_staff)

    def test_total_spent_is_0_when_customer_has_no_paid_orders(self):
        Customer = apps.get_model('customers', 'Customer')
        customer = Customer.objects.create_superuser('foo@example.com', 'First', 'Last', 'mypass')
        self.assertEquals(customer.amount_spent, 0)

    def test_total_spent_is_greater_than_zero_when_customer_has_at_least_one_paid_order(self):
        customer = CustomerFactory()
        OrderFactory(customer=customer, charged_amount=Decimal('12'), payment_status='paid')
        self.assertEquals(customer.amount_spent, Decimal('12'))

    def test_can_retrieve_number_of_orders(self):
        customer = CustomerFactory()
        OrderFactory(customer=customer, charged_amount=Decimal('12'), payment_status='paid')
        self.assertEquals(customer.number_of_orders, 1)


class CustomerChildModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.parent = CustomerFactory()
        return super().setUpTestData()

    # def test_can_get_age_in_months_for_child_that_is_18_months_old(self):
    #     current_date = timezone.now().date()
    #     one_year_six_months_ago = current_date - relativedelta(years=1, months=6)
    #     child = CustomerChildFactory(birth_date=one_year_six_months_ago, parent=self.parent)
    #     self.assertEqual(child.age_in_months, 18)

    def test_can_get_child_full_name_with_property(self):
        child = CustomerChildFactory(parent=self.parent)
        self.assertIsNotNone(child.full_name)

    def test_will_create_a_cart_for_a_new_child(self):
        with self.captureOnCommitCallbacks(execute=True):
            child = CustomerChildFactory(parent=self.parent)
        self.assertIsNotNone(child.cart)


class CustomerSubscriptionModelTestSuite(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = CustomerFactory()
        cls.child = CustomerChildFactory(parent=cls.customer)
        cls.ingredient = IngredientFactory(name='Some Ingredient')
        cls.product = ProductFactory(title='Recipe 1', product_type='recipe', ingredients=[cls.ingredient])

    def setUp(self) -> None:
        self.subscription = CustomerSubscriptionFactory(
            customer=self.customer,
            customer_child=self.child
        )

    def test_can_retrieve_line_items(self):
        cart = CartFactory(customer=self.customer, customer_child=self.child)
        line_item = CartLineItemFactory(cart=cart, product=self.product, quantity=12)
        self.assertEqual(self.subscription.line_items.first().product, line_item.product)

    def test_will_display_subscription_value_amount(self):
        cart = CartFactory(customer_child=self.subscription.customer_child, customer=self.subscription.customer)
        CartLineItemFactory(cart=cart, quantity=24, )
        self.subscription.number_of_servings = 24
        self.subscription.save()
        self.subscription.refresh_from_db()

        self.assertEqual(self.subscription.amount, sum([
            line_item.product_variant.price * line_item.quantity
            for line_item in self.subscription.line_items
        ]))

    def test_will_set_next_order_charge_date_when_activated_and_has_no_next_order_charge_date(self):
        subscription = CustomerSubscriptionFactory(is_active=False)
        current_datetime = timezone.now()
        with freeze_time(time_to_freeze=current_datetime):
            with mock.patch(
                'apps.customers.models.customer_subscription.CustomerSubscription._create_order',
                side_effect=lambda: True,
            ):
                subscription.activate()
                subscription.save()
            next_date = (current_datetime + timedelta(days=subscription.frequency * 7)).date()
        self.assertEquals(subscription.next_order_charge_date, next_date)

    def test_will_not_create_order_if_specified(self):
        subscription = CustomerSubscriptionFactory(is_active=False)
        current_datetime = timezone.now()
        with freeze_time(time_to_freeze=current_datetime):
            with mock.patch(
                    'apps.customers.models.customer_subscription.CustomerSubscription._create_order',
                    side_effect=lambda: True,
            ) as mocked:
                subscription.activate(create_order=False)
                subscription.save()
        self.assertFalse(mocked.called)

    def test_next_order_changes_enabled_date_get_set_when_next_order_charge_date_is_changed(self):
        subscription = CustomerSubscriptionFactory(is_active=True)
        today = timezone.now().date()
        subscription.next_order_charge_date = today + timedelta(days=3)
        subscription.save()
        subscription.refresh_from_db()
        self.assertEquals(subscription.next_order_changes_enabled_date, today + timedelta(days=2))

    def test_next_order_changes_enabled_date_get_blanked_when_next_order_charge_date_is_blanked(self):
        subscription = CustomerSubscriptionFactory(is_active=True)
        subscription.next_order_charge_date = None
        subscription.save()

        self.assertEquals(subscription.next_order_changes_enabled_date, None)

    def test_will_unset_next_order_charge_date_when_deactivated(self):
        subscription = CustomerSubscriptionFactory(is_active=False)
        current_datetime = timezone.now()
        with freeze_time(time_to_freeze=current_datetime):
            with mock.patch(
                    'apps.customers.models.customer_subscription.CustomerSubscription._create_order',
                    side_effect=lambda: True,
            ):
                subscription.activate()
                subscription.save()

            subscription.deactivate()
            subscription.save()

        self.assertEquals(subscription.next_order_charge_date, None)

    def test_will_send_subscription_cancellation_email_when_deactivate(self):
        subscription = CustomerSubscriptionFactory(is_active=True, status='active')
        with self.captureOnCommitCallbacks(execute=True):
            with mock.patch(
                'apps.customers.models.customer_subscription.'
                'CustomerSubscription._send_subscription_cancellation_notification'
            ) as mocked:
                subscription.deactivate()
                subscription.save()
        self.assertTrue(mocked.called)

    def test_will_pause_customer_subscription(self):
        subscription = CustomerSubscriptionFactory(is_active=True, status='active', frequency=2)
        current_datetime = timezone.now()
        with freeze_time(time_to_freeze=current_datetime):
            subscription.pause()
        subscription.save()

        two_weeks_from_today = current_datetime + timedelta(days=14)
        self.assertEquals(subscription.paused_at, current_datetime)
        self.assertEquals(subscription.next_order_charge_date, two_weeks_from_today)
        self.assertEquals(subscription.next_order_changes_enabled_date, two_weeks_from_today - timedelta(days=1))
        self.assertEquals(subscription.status, SubscriptionStatusEnum.paused)

    def test_will_pause_customer_subscription_with_custom_date(self):
        subscription = CustomerSubscriptionFactory(is_active=True, status='active', frequency=4)
        current_datetime = timezone.now()
        one_week_from_today = current_datetime + timedelta(days=7)
        with freeze_time(time_to_freeze=current_datetime):
            subscription.pause(one_week_from_today)
        subscription.save()

        self.assertEquals(subscription.paused_at, current_datetime)
        self.assertEquals(subscription.next_order_charge_date, one_week_from_today)
        self.assertEquals(subscription.next_order_changes_enabled_date, one_week_from_today - timedelta(days=1))
        self.assertEquals(subscription.status, SubscriptionStatusEnum.paused)
