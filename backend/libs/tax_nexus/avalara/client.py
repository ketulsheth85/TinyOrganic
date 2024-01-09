from decimal import Decimal
from typing import Union
from uuid import uuid4 as uuid

from django.apps import apps
from django.utils import timezone

from apps.addresses.models import Location
from apps.orders.libs import PaymentCalculator
from libs.tax_nexus.avalara.avalara_client import AvalaraClient
from libs.tax_nexus.client import TaxClient


class CouldNotCalculateTaxForPurchaseError(Exception):
    ...


class CouldNotRecordTaxForPurchaseError(Exception):
    ...


class CouldNotRecordTaxForRefundError(Exception):
    ...


class TaxProcessorClient(TaxClient):
    def __init__(self, *args, **kwargs):
        self.client = AvalaraClient
        self.customer_discount: Union[None, 'Discount'] = None
        self.shipping_rate: 'ShippingRate' = None
        self.paymentCalculator: 'PaymentCalculator' = PaymentCalculator()

    def set_customer_discount(self, customer_discount: 'Discount'):
        self.customer_discount = customer_discount
        return self

    def set_shipping_rate(self, shipping_rate: 'ShippingRate'):
        self.shipping_rate = shipping_rate
        return self

    def calculate_tax(self, cart: 'Cart'):
        '''
        Calculates tax, but does not record a charge,
        strongly recommended that this method is called
        after customer address has been verified :)
        '''

        order_id = str(uuid())
        # SalesOrder: A quote for a potential sale
        response = self._create_sales_document(cart, 'SalesOrder', str(order_id))

        if response.get('error'):
            raise CouldNotCalculateTaxForPurchaseError(
                f'Could calculate tax for cart #{cart.id}',
                f'cart: {cart}',
                response.get('error')
            )
        return {
            'total_tax': Decimal(response.get('totalTax')),
            'tax_rate': sum([summary['rate'] for summary in response.get('summary', [])]) * 100
        }

    def charge(self, cart: 'Cart', order_id):
        '''
        Calulates tax, and records taxable transaction,
        strongly recommended that this method is called
        after customer address has been verified :)
        '''

        # SalesInvoice: A finalized sale made to a customer
        response = self._create_sales_document(cart, 'SalesInvoice', str(order_id))
        if response.get('error'):
            raise CouldNotRecordTaxForPurchaseError(
                f'Could not record taxable charge to Avalara for order #{order_id}',
                response.get('error')
            )
        return {
            'total_tax': Decimal(response.get('totalTax'))
        }

    def refund(self, order_id):
        response = self.client.refund_transaction('DEFAULT', str(order_id), {
            "refundTransactionCode": str(order_id),
            "refundDate": self._get_current_date(),
            "refundType": "Full",
            "referenceCode": f"refund for order #{order_id}"
        })
        data = response.json()

        if data.get('error'):
            raise CouldNotRecordTaxForRefundError(
                f'Could taxable refund to Avalara for order #{order_id}',
                data.get('error')
            )
        return data

    def validate_tax_address(self, address: 'Location'):
        response = self.client.resolve_address_post(self._parse_address(address))

        data = response.json()
        message_list = data.get('messages')
        messages = []

        if message_list:
            messages = [message.get('summary') for message in message_list]
        return {
            'valid_address': not bool(message_list),
            'messages': messages
        }

    def _is_sales_document(self, transaction_type):
        """
        Checks if tax is being calculated for a purchase order, if not we assume it's for
        an estimate, note that code will have to be updated if we start using more than two
        document types
        """
        return transaction_type == 'SalesInvoice'

    def _initialize_payment_calculator(self, cart: 'Cart', transaction_type, order_id):
        Order = apps.get_model('orders', 'Order')
        if self._is_sales_document(transaction_type):
            order = Order.objects.get(id=order_id)
            self.paymentCalculator = self.paymentCalculator.from_order(order)
        else:
            self.paymentCalculator = self.paymentCalculator.from_cart(cart)

    def _get_line_items(self, cart: 'Cart', transaction_type, order_id):
        if self._is_sales_document(transaction_type):
            Order = apps.get_model('orders', 'Order')
            order = Order.objects.get(id=order_id)
            line_items = order.line_items.filter()
        else:
            line_items = cart.line_items.filter()

        return line_items

    def _create_sales_document(self, cart: 'Cart', transaction_type, order_id):
        """
         Info on document types here:
         https://developer.avalara.com/ecommerce-integration-guide/sales-tax-badge/transactions/simple-transactions/document-types/
        """

        # initialize payment calculator
        self._initialize_payment_calculator(cart, transaction_type, order_id)

        customer = cart.customer
        address = Location.objects \
            .filter(customer=customer.id) \
            .latest('created_at')
        is_valid_location = self.validate_tax_address(address)

        # calculate taxes on zip + state if address cannot be confirmed
        ship_to = self._parse_address(address)
        if not is_valid_location.get('valid_address'):
            ship_to['line1'] = 'GENERAL DELIVERY'

        # get proper line items based on transaction type
        line_items = self._get_line_items(cart, transaction_type, order_id)

        response = self.client.create_transaction({
            'code': order_id,
            'date': self._get_current_date(),
            'lines': self._parse_line_items(line_items),
            'addresses': {
                'shipFrom': self._resolve_ship_from_location(address),
                'shipTo': ship_to
            },
            'type': transaction_type,
            'customerCode': str(customer.id),
            'commit': True
        })
        return response.json()

    def _parse_address(self, address: 'Location'):
        return {
            'line1': address.street_address,
            'city': address.city,
            'region': address.state,
            'country': 'us',
            'postalCode': str(address.zipcode)
        }

    def _parse_line_items(self, line_items):
        items = [
            {
                'description': line_item.product.title,
                'quantity': line_item.quantity,
                'amount': float(line_item.product_variant.price * line_item.quantity),
                'itemCode': line_item.product_variant.sku_id
            }
            for line_item in line_items
        ]

        items.append({
            'description': self.shipping_rate.title,
            'quantity': 1,
            'amount': float(self.shipping_rate.price),
            'itemCode': str(self.shipping_rate.id)
        })

        # apply 24 pack discount
        if self.paymentCalculator.is_24_pack():
            items.append({
                'description': '24 pack discount',
                'quantity': 1,
                'amount': -20.00,
                'itemCode': 'TWENTY_FOUR_PACK_DISCOUNT'
            })

        # apply coupon discount
        if self.paymentCalculator.coupon_discount_amount:
            discount_amount = self.paymentCalculator.coupon_discount_amount
            items.append({
                'description': f'{self.customer_discount.discount if self.customer_discount else ""}',
                'quantity': 1,
                'amount': float(discount_amount * -1),
                'itemCode': self.customer_discount.discount.codename if self.customer_discount else 'NO_DISCOUNT_CODE'
            })

        return items

    def _get_current_date(self):
        now = timezone.now()
        return now.strftime('%Y-%m-%d')

    def _resolve_ship_from_location(self, address: 'Location'):
        # return default tax location in Avalara, defaults to company hq unless someone changed it on Avalara
        return {
            'locationCode': 'DEFAULT'
        }
