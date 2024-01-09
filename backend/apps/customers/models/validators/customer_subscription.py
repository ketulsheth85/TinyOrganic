from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_charge_date(value):
    if value is None:
        return
    now = timezone.now().date()
    latest_valid_charge_date = now + timedelta(61)

    if  value < now or value > latest_valid_charge_date:
        raise ValidationError("Date must be between tomorrow and 61 days out")
