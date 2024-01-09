from decimal import Decimal

from libs.tax_nexus.client import TaxClient


class MockTaxProcessorClient(TaxClient):
    def __init__(self, *args, **kwargs):
        ...

    def calculate_tax(self, cart: 'Cart'):
        return {
            'status_code': 200,
            'error': '',
            'total_tax': Decimal(0.0)
        }

    def charge(self, cart: 'Cart', order_id):
        return {
            'status_code': 200,
            'error': '',
            'total_tax': 0.0
        }

    def refund(self, order_id):
        ...

    def validate_tax_address(self, address: 'Location'):

        return {
            'valid_address': True,
            'messages': []
        }