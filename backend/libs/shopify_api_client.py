from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Union

import shopify
from dataclasses_json import dataclass_json
from django.conf import settings


@dataclass_json
@dataclass
class LineItemDTO:
    variant_id: str
    quantity: int
    sku: str
    price: str


@dataclass_json
@dataclass
class RefundLineItemDTO(LineItemDTO):
    restock_type: str


@dataclass_json
@dataclass
class AddressDTO:
    address1: str
    city: str
    zip: str
    address2: Union[None, str] = ''
    country: str = 'United States'
    province_code: Union[None, str] = ''


@dataclass_json
@dataclass
class ShippingAddressDTO(AddressDTO):
    first_name: str = ''
    last_name: str = ''


@dataclass_json
@dataclass
class CustomerDTO:
    first_name: str
    last_name: str
    email: str
    phone: Union[None, str] = None
    addresses: Union[List[AddressDTO], None] = None


@dataclass_json
@dataclass
class ShippingRateDTO:
    price: str
    title: str


@dataclass_json
@dataclass
class DiscountDTO:
    code: str
    amount: str
    type: str


@dataclass_json
@dataclass
class TaxLineDTO:
    price: str
    rate: str
    title: str


@dataclass_json
@dataclass
class ShopifyOrderCreateDTO:
    line_items: List[LineItemDTO]
    customer: CustomerDTO
    shipping_address: AddressDTO
    shipping_lines: List[ShippingRateDTO]
    email: str
    financial_status: str
    discount_codes: Union[None, List[DiscountDTO]]
    tags: List[str] = list
    total_tax: str = ''
    tax_lines: List = list
    send_receipt: bool = False


class CouldNotSyncOrderError(Exception):
    ...


class CouldNotSyncRefundError(Exception):
    ...


class CouldNotCreateRefundInShopifyStoreError(Exception):
    ...


class CouldNotApplyRefundError(Exception):
    ...


class CouldNotCreateTransactionError(Exception):
    ...


class CouldNotCancelOrderError(Exception):
    ...


class ShopifyAPIClient:
    def __init__(self):
        self.shop_url = settings.SHOPIFY_DOMAIN
        self.api_version = settings.SHOPIFY_API_VERSION
        self.api_key = settings.SHOPIFY_API_KEY
        self.secret = settings.SHOPIFY_API_KEY_SECRET
        self.password = settings.SHOPIFY_PASSWORD

    def _calculate_sales_tax_rate(self, order):
        pre_tax_price = order.charged_amount - order.tax_total
        if pre_tax_price < 1:
            return '0'

        decimal_tax_rate = Decimal(f'{order.tax_total / pre_tax_price}')
        return str(float(decimal_tax_rate))

    def _calculate_line_item_price(self, line_item: 'OrderLineItem', order_is_24_pack):
        item_price = f'{line_item.product_variant.price}'

        if order_is_24_pack and line_item.product.product_type == 'recipe':
            item_price = str(Decimal(f'{float(line_item.product_variant.price) - 20 / 24}'))

        return item_price

    def _build_order_data(self, order):
        line_items = order.line_items.filter()
        customer = order.customer
        address = customer.addresses.first()
        shipping_rate = order.shipping_rate

        if not address:
            raise CouldNotSyncOrderError(f'Customer {customer} has no Address. Cannot ship.')

        if not shipping_rate:
            raise CouldNotSyncOrderError(
                f'Order {order.id} - {order.customer.email} has no shipping rate. Cannot Ship.'
            )
        discount_data = []
        if order.applied_discount is not None:
            discount_data = [
                DiscountDTO(
                    code=order.applied_discount.discount.codename,
                    type='_'.join(order.applied_discount.discount.discount_type.split(' ')),  # "fixed amount" -> "fixed_amount"
                    amount=f'{order.applied_discount.discount.amount}',
                ).to_dict()
            ]

        order_is_24_pack = order.is_24_pack()

        items_data = [
            LineItemDTO(
                variant_id=line_item.product_variant.external_variant_id,
                quantity=line_item.quantity,
                sku=line_item.product_variant.sku_id,
                price=self._calculate_line_item_price(line_item, order_is_24_pack)
            ).to_dict() for line_item in line_items
        ]

        customer_data = CustomerDTO(
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
        ).to_dict()
        shipping_address_data = ShippingAddressDTO(
            first_name=customer.first_name,
            last_name=customer.last_name,
            address1=address.street_address,
            address2='',
            city=address.city,
            province_code=address.state,
            zip=address.zipcode,
        ).to_dict()
        shipping_lines_data = [
            ShippingRateDTO(
                price=str(shipping_rate.price),
                title=shipping_rate.title,
            ).to_dict()
        ]

        tax_lines_data = []
        if order.tax_total:
            tax_lines_data = [
                TaxLineDTO(
                    price=str(order.tax_total),
                    rate=str(self._calculate_sales_tax_rate(order)),
                    title='Tax'
                ).to_dict()
            ]
        return ShopifyOrderCreateDTO(
            line_items=items_data,
            customer=customer_data,
            shipping_address=shipping_address_data,
            shipping_lines=shipping_lines_data,
            email=customer.email,
            financial_status=str(order.payment_status),
            tags=order.tags or ['From Re-platform'],
            discount_codes=discount_data,
            tax_lines=tax_lines_data,
        ).to_dict()

    def _create_transaction_for_order(self, shopify_order_id: str):
        transaction = shopify.Transaction({
                'kind': 'sale',
                'source': 'external'
            },
            prefix_options={'order_id': shopify_order_id}
        )
        transaction.save()
        if transaction.errors.errors:
            raise CouldNotCreateTransactionError(
                f'Could not record transaction for order: {shopify_order_id}'
            )
        return transaction

    def create_order(self, order: 'Order'):
        create_order_payload = self._build_order_data(order)
        with shopify.Session.temp(self.shop_url, self.api_version, self.password):
            shopify_order = shopify.Order.create(create_order_payload)
            if shopify_order.errors.errors:
                raise CouldNotSyncOrderError(f'Order ID: {order.id}', shopify_order.errors.errors)

        return shopify_order

    def create_transaction_for_order(self, shopify_order_id: str):
        with shopify.Session.temp(self.shop_url, self.api_version, self.password):
            try:
                self._create_transaction_for_order(shopify_order_id)
            except CouldNotCreateTransactionError:
                raise

    def retrieve_customer_with_shopify_id(self, shopify_customer_id: str):
        with shopify.Session.temp(self.shop_url, self.api_version, self.password):
            return shopify.Customer.find(shopify_customer_id)

    def create_customer(self, customer: 'Customer'):
        with shopify.Session.temp(self.shop_url, self.api_version, self.password):
            address = customer.addresses.first()
            shopify_customer = shopify.Customer.create({
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "email": customer.email,
                "phone": f'{customer.phone_number.replace("+", "")}',
                "addresses": [
                    {
                        "address1": address.street_address,
                        "address2": '',
                        "city": address.city,
                        "province_code": address.state,
                        "zip": address.zipcode,
                        "country": "United States",
                    }
                ],
            })
            return shopify_customer

    def retrieve_order(self, shopify_order_id: str):
        with shopify.Session.temp(self.shop_url, self.api_version, self.password):
            return shopify.Order.find(shopify_order_id)

    def _send_calculate_refund_request(self, shopify_order_id: str, order_line_items_data: List[Dict]):
        calculated_refund = shopify.Refund.calculate(
            shopify_order_id,
            refund_line_items=order_line_items_data
        )
        if calculated_refund.errors.errors:
            raise CouldNotSyncRefundError(
                'Could not calculate refund before applying',
                f' Shopify order ID: {shopify_order_id}',
                calculated_refund.errors.errors
            )
        return calculated_refund

    def _create_refund(self, shopify_order_id: str, order_line_items_data: List[Dict]):
        refund_obj = shopify.Refund(
            {
                "notify": True,
                "shipping": {
                    "full_refund": True,
                },
                "currency": "USD",
                "refund_line_items": order_line_items_data
            },
            prefix_options={'order_id': shopify_order_id}
        )
        if refund_obj.errors.errors:
            raise CouldNotCreateRefundInShopifyStoreError(
                f'Shopify Order ID: {shopify_order_id}',
                refund_obj.errors.errors
            )
        refund_obj.save()

    def _apply_refund_to_order(self, shopify_order: shopify.Order, refund_object: shopify.Refund):
        shopify_order.financial_status = 'refunded'
        shopify_order.refunds = [refund_object]
        shopify_order.save()
        if shopify_order.errors.errors:
            raise CouldNotApplyRefundError()
        return shopify_order

    def _create_refund_transaction(self, shopify_order: shopify.Order, amount: str = ''):
        with shopify.Session.temp(self.shop_url, self.api_version, self.password):
            refund_transaction = shopify.Transaction({
                'kind': 'refund',
                'parent_id': shopify_order.transactions()[0].id
            }, prefix_options={'order_id': shopify_order.id})

            if amount:
                refund_transaction.amount = amount

            refund_transaction.save()
            if refund_transaction.errors.errors:
                raise CouldNotCreateTransactionError(
                    f'Could not record refund transaction for order: {shopify_order.id}'
                )
            return refund_transaction

    def _create_partial_refund(self, shopify_order_id: str):
        refund_obj = shopify.Refund(
            {
                'notify': True,
            }, prefix_options={'order_id': shopify_order_id}
        )
        with shopify.Session.temp(self.shop_url, self.api_version, self.password):
            refund_obj.save()
        return refund_obj

    def partially_refund_order(self, order: 'Order'):
        shopify_order = self.retrieve_order(order.external_order_id)
        try:
            self._create_refund_transaction(shopify_order, f'{order.refunded_amount}')
        except CouldNotCreateTransactionError:
            raise

        return self._create_partial_refund(shopify_order.id)

    def refund_order(self, order: 'Order'):
        shopify_order = self.retrieve_order(order.external_order_id)
        with shopify.Session.temp(self.shop_url, self.api_version, self.password):
            order_line_items_data = [
                {
                    "line_item_id": line_item.id,
                    "quantity": line_item.quantity,
                    "restock_type": 'no_restock',
                } for line_item in shopify_order.line_items
            ]
            try:
                refund_obj = self._send_calculate_refund_request(order.external_order_id, order_line_items_data)
            except (CouldNotSyncRefundError, CouldNotCreateRefundInShopifyStoreError):
                raise

            try:
                shopify_order = self._apply_refund_to_order(shopify_order, refund_obj)
            except CouldNotApplyRefundError:
                raise

            try:
                self._create_refund_transaction(shopify_order)
            except CouldNotCreateTransactionError:
                raise

            return shopify_order

    def cancel_order(self, order: 'Order'):
        shopify_order = self.retrieve_order(order.external_order_id)
        with shopify.Session.temp(self.shop_url, self.api_version, self.password):
            shopify_order.cancel()
            shopify_order.save()

        if not shopify_order.attributes['cancelled_at']:
            raise CouldNotCancelOrderError(f'Could not cancel order {order} with shopify id: {shopify_order}')

        return shopify_order
