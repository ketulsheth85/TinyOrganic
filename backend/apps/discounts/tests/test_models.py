from django.test import TestCase

from apps.discounts.tests.factories import CustomerDiscountFactory


class CustomerDiscountModelTestSuite(TestCase):
    def setUp(self) -> None:
        self.customer_discount = CustomerDiscountFactory()

    def test_will_deactivate_after_discount_has_reached_redemption_limit(self):
        self.customer_discount.redeem()
        self.customer_discount.save()
        self.assertFalse(self.customer_discount.is_active)

    def test_will_not_deactivate_if_discount_has_not_reached_redemption_limit(self):
        self.assertTrue(self.customer_discount.is_active)
