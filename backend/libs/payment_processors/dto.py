from dataclasses import dataclass
from decimal import Decimal
from typing import Union


@dataclass
class BaseTransactionDTO:
    decimal_amount: Union[None, Decimal] = None
    cents_amount: Union[None, int] = None
    processor_payment_method_id: Union[None, str] = None
    processor_transaction_id: Union[None, str] = None
    payment_intent: Union[None, str] = None

    def dollar_amount_to_cents(self) -> int:
        return int(self.decimal_amount * 100) if self.decimal_amount else 0

    def cents_amount_to_decimal_amount(self):
        return Decimal(f'{self.cents_amount / 100}')


@dataclass
class PaymentMethodAttachmentDTO:
    processor_customer_id: str
    processor_payment_method_id: str


@dataclass
class ChargeDTO(BaseTransactionDTO):
    processor_customer_id: str = None
    capture_immediately: bool = True
    currency_code: str = 'usd'


@dataclass
class ProcessedChargeDTO(BaseTransactionDTO):
    customer_id: Union[None, str] = None
    payment_method_id: Union[None, str] = None
    is_captured: Union[None, bool] = True


@dataclass
class RefundDTO(BaseTransactionDTO):
    reason: Union[None, str] = 'requested_by_customer'


@dataclass
class ProcessedRefundDTO(BaseTransactionDTO):
    customer_id: Union[None, str] = None
    customer_payment_method_id: Union[None, str] = None
