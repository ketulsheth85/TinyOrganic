from datetime import timedelta

from django.test import SimpleTestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.customers.models.validators.customer_subscription import validate_charge_date


class ValidatorTestSuite(SimpleTestCase):

    def test_charge_validator_accepts_valid_date(self):
        date_obj = timezone.now().date() + timedelta(days=1)

        self.assertEquals(validate_charge_date(date_obj), None)

    def test_charge_validator_rejects_invalid_date(self):
        date_obj = timezone.now().date() + timedelta(days=80)

        with self.assertRaises(ValidationError):
            self.assertEquals(validate_charge_date(date_obj), None)

