from abc import abstractmethod


class TaxClient:
    @abstractmethod
    def charge(self, cart: 'Cart', order_id):
        ...

    @abstractmethod
    def refund(self, order_id):
        ...

    @abstractmethod
    def validate_tax_address(self, address: 'Location'):
        ...
