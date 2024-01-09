from decimal import Decimal

from django.test import SimpleTestCase
from libs.helpers import ModelChoiceEnum, decimal_to_cents


class TestModelEnum(ModelChoiceEnum):
    one = 1
    two = 2


class HelpersTestSuite(SimpleTestCase):
    def test_can_retrieve_enums_as_model_choice_tuple(self):
        result = TestModelEnum.as_choices()
        self.assertEqual(result._doubles, [(1, 1), (2, 2)])

    def test_will_convert_decimal_value_to_correct_cent_amount(self):
        self.assertEqual(decimal_to_cents(Decimal('10')), 1000)

    def test_will_convert_fractional_dollar_amount_to_correct_cent_amount(self):
        self.assertEqual(decimal_to_cents(Decimal('10.15')), 1015)
