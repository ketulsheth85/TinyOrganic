"""
A subclass of Enum that makes it easy to create a set of constants (think
status fields with multiple statuses) and encapsulate them in one data
structure. Makes it easier and cleaner to import. Most useful as a way
to generate an above Choices list for model fields.
"""
from decimal import Decimal
from enum import Enum, unique

from model_utils import Choices


@unique
class ModelChoiceEnum(Enum):
    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == other

    @classmethod
    def as_choices(cls):
        return Choices(*[choice.value for choice in cls])


def decimal_to_cents(decimal_amount: Decimal) -> int:
    return int(decimal_amount * 100)
