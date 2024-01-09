from abc import abstractmethod

from libs.payment_processors.dto import ChargeDTO, PaymentMethodAttachmentDTO, RefundDTO


class PaymentProcessorClient:
    @abstractmethod
    def charge(self, amount: ChargeDTO):
        ...

    @abstractmethod
    def create_customer(self):
        ...

    @abstractmethod
    def refund(self, refund_data: RefundDTO):
        ...

    @abstractmethod
    def retrieve_customer(self, customer_obj: 'Customer'):
        ...

    def attach_customer_to_payment_method(self, attachment_data: PaymentMethodAttachmentDTO):
        ...
