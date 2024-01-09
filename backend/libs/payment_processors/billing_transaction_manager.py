from abc import abstractmethod
from typing import Union

from libs.payment_processors.dto import ChargeDTO, ProcessedRefundDTO


class BillingTransactionManager:
    def __init__(
        self,
        processed_charge_dto: Union[None, ChargeDTO] = None,
        processed_refund_dto: Union[None, ProcessedRefundDTO] = None,
    ):
        self.processed_charge_data = processed_charge_dto
        self.processed_refund_data = processed_refund_dto

    @abstractmethod
    def save_charge_to_database(self):
        ...

    @abstractmethod
    def save_refund_to_database(self):
        ...
