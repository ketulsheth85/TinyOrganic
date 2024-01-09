from datetime import timedelta
from unittest import mock
from django.utils import timezone
from django.test import TestCase

from apps.customers.tasks import (
    send_upcoming_charge_notification_to_active_subscribers
)
from apps.customers.tests.factories import CustomerSubscriptionFactory


# class CustomerTaskTestSuite(TestCase):
#     def test_will_send_notification_email_to_active_subscribers_with_upcoming_orders(self):
#         CustomerSubscriptionFactory(is_active=True, next_order_charge_date=timezone.now().date() + timedelta(days=3))
#         with mock.patch('apps.customers.tasks._send_email.delay') as mocked:
#             send_upcoming_charge_notification_to_active_subscribers()
#
#         self.assertTrue(mocked.called)
