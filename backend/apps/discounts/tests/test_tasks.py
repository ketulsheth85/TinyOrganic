import os
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from apps.customers.tests.factories import CustomerFactory
from apps.discounts.models import Discount
from apps.discounts.tasks import deactivate_expired_discount_codes, \
    create_customer_referral_coupon_from_loyalty_client
from apps.discounts.tests.factories import DiscountFactory
from libs.yotpo_client import CouldNotGetYotpoCustomerError


def _mock_partial_yotpo_customer_response(*args, **kwargs):
    return {
        'referral_code': {
            'code': kwargs.get('discount_code', 'RANDNUM')
        }
    }


def _mock_cannot_create_yotpo_customer_response(*args, **kwargs):
    return CouldNotGetYotpoCustomerError('customer does not exist')


class DiscountTasksTestCase(TestCase):
    def setUp(self) -> None:
        self.expiring_discount = DiscountFactory(
            is_active=True,
            deactivate_at=timezone.now()
        )
        self.activate_discount = DiscountFactory(
            is_active=False,
            activate_at=timezone.now()
        )

    def test_will_deactivate_expiring_discount_codes(self):
        deactivate_expired_discount_codes()
        self.expiring_discount.refresh_from_db()
        self.assertFalse(self.expiring_discount.is_active)

    # def test_will_activate_queued_discount_codes(self):
    #     activate_inactive_discount_codes()
    #     self.activate_discount.refresh_from_db()
    #     self.assertTrue(self.activate_discount.is_active)

    # TODO: figure out why CI won't run these tests... For now, uncomment before committing and ensure that tests pass.
    # def test_will_create_discount_code_for_customer_without_yotpo_account(self):
    #     customer = CustomerFactory()
    #     with mock.patch(
    #         'libs.yotpo_client.YotpoClient.create_customer',
    #         side_effect=_mock_partial_yotpo_customer_response,
    #     ):
    #         create_customer_referral_coupon_from_loyalty_client(str(customer.id))
    #
    #     customer_discount = Discount.objects.get(codename='RANDNUM')
    #     self.assertEqual(customer_discount.from_yotpo, True)

#     def test_will_not_create_discount_code_for_existing_yotpo_discount(self):
#         customer = CustomerFactory()
#         discount_code = 'RANDNUM'
#         DiscountFactory(referrer=customer, codename='RANDNUM', from_yotpo=True)
#
#         with mock.patch(
#             'libs.yotpo_client.YotpoClient.get_customer',
#             side_effect=_mock_partial_yotpo_customer_response,
#         ):
#             create_customer_referral_coupon_from_loyalty_client(str(customer.id))
#
#             customer_discount = Discount.objects.get(codename=discount_code)
#             self.assertEqual(customer_discount.codename, discount_code)
#             self.assertEqual(customer_discount.from_yotpo, True)
