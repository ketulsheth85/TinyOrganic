from dataclasses import dataclass
from decimal import Decimal
from typing import List, Union

from django.apps import apps
from django.db.models import Sum

from libs.helpers import ModelChoiceEnum


class OrderFulfillmentStatusEnum(ModelChoiceEnum):
    pending = 'pending'
    partially_fulfilled = 'partial'
    fulfilled = 'fulfilled'
    cancelled = 'cancelled'


class OrderPaymentStatusEnum(ModelChoiceEnum):
    pending = 'pending'
    failed = 'failed'
    authorized = 'authorized'
    partially_paid = 'partially_paid'
    paid = 'paid'
    partially_refunded = 'partially_refunded'
    refunded = 'refunded'
    voided = 'voided'


class OrderSyncedToShopifyStatusEnum(ModelChoiceEnum):
    synced = 'synced'
    pending = 'pending'


class OrderConfirmationEmailStatus(ModelChoiceEnum):
    sent = 'sent'
    unsent = 'unsent'


class CannotBuildOrderError(Exception):
    ...


@dataclass
class OrderSummaryDetailDTO:
    cart: 'Cart'
    customer_discount: Union[None, 'CustomerDiscount'] = None
    shipping_rate: Union[None, 'ShippingRate'] = None
    tax_amount: Decimal = Decimal('0')


class PaymentCalculator:
    def __init__(self):
        self.subtotal_amount = Decimal('0')
        self.running_subtotal_amount = Decimal('0')
        self.coupon_discount_amount = Decimal('0')
        self.discount_total_amount = Decimal('0')
        self.amount_total = Decimal('0')
        self.tax_total = Decimal('0')
        self.shipping_rate = None
        self.order = None
        self.cart = None
        self.applied_discount = None
        self.line_items = None

    def set_tax(self, tax_total: 'Decimal'):
        self.tax_total = tax_total
        return self

    def set_shipping_rate(self, shipping_rate: 'ShippingRate'):
        self.shipping_rate = shipping_rate
        return self

    def set_cart(self, cart: 'Cart'):
        self.cart = cart
        self.line_items = cart.line_items.filter()
        return self

    def set_applied_discount(self, applied_discount: 'CustomerDiscount'):
        self.applied_discount = applied_discount
        return self

    def set_order(self, order: 'Order'):
        self.order = order
        self.line_items = order.line_items.filter()
        return self

    @classmethod
    def summary(cls, order_summary_detail_dto: OrderSummaryDetailDTO):
        calculations = cls()\
            .set_tax(order_summary_detail_dto.tax_amount)\
            .set_cart(order_summary_detail_dto.cart)\
            .set_shipping_rate(order_summary_detail_dto.shipping_rate)\
            .set_applied_discount(order_summary_detail_dto.customer_discount)\
            .calculate()
        return {
            'shipping': order_summary_detail_dto.shipping_rate.price,
            'taxes': order_summary_detail_dto.tax_amount,
            'discounts': calculations.discount_total_amount,
            'subtotal': calculations.subtotal_amount,
            'total': calculations.amount_total,
        }

    @classmethod
    def from_cart(cls, cart):
        ShippingRate = apps.get_model('orders', 'ShippingRate')
        CustomerDiscount = apps.get_model('discounts', 'CustomerDiscount')
        return cls()\
            .set_cart(cart)\
            .set_applied_discount(CustomerDiscount.objects.filter(customer=cart.customer, is_active=True).first())\
            .set_shipping_rate(ShippingRate.objects.filter(is_default=True).first())\
            .calculate()

    @classmethod
    def from_order(cls, order):
        return cls()\
            .set_order(order)\
            .set_tax(order.tax_total)\
            .set_shipping_rate(order.shipping_rate)\
            .set_applied_discount(order.applied_discount)\
            .calculate()

    def get_subtotal(self):
        return sum([
            line_item.quantity * line_item.product_variant.price
            for line_item in self.line_items.filter()
        ])

    def get_number_of_servings(self):
        return sum([
            line_item.quantity if line_item.product.product_type == 'recipe' else 0
            for line_item in self.line_items
        ])

    def _get_discount_amount(self):
        discount_amount = 0
        if self.applied_discount:
            discount = self.applied_discount.discount
            if discount.discount_type == 'percentage':
                discount_amount = (self.running_subtotal_amount * discount.amount) / 100
            else:
                discount_amount = discount.amount

        return discount_amount

    def apply_discount_to_running_subtotal(self):
        discount_amount = self._get_discount_amount()
        self.coupon_discount_amount = discount_amount
        self.running_subtotal_amount -= discount_amount

    def is_24_pack(self):
        return self.get_number_of_servings() >= 24

    def calculate(self):

        # 1: calculate subtotal for cart
        self.subtotal_amount = self.get_subtotal()
        self.running_subtotal_amount = self.subtotal_amount
        # 2: apply discounts

        # automatic $20 discount for 24-packs
        if self.is_24_pack():
            self.running_subtotal_amount -= Decimal('20')

        # apply the customer discount code to the running subtotal
        self.apply_discount_to_running_subtotal()

        # 3: apply shipping
        self.amount_total = self.running_subtotal_amount + self.shipping_rate.price

        # 4: apply tax
        self.amount_total += self.tax_total
        self.discount_total_amount = self.subtotal_amount - self.running_subtotal_amount

        return self


class OrderBuilder:
    def __init__(self, *args, **kwargs):
        self.customer = None
        self.customer_child = None
        self.number_of_servings = None
        self.line_items = []
        self.order = None
        self.shipping_rate = None
        self.tax_amount = Decimal('0')
        self.customer_discount = None
        self.discount_amount = Decimal('0')
        self.total_amount = Decimal('0')
        self.subtotal_amount = Decimal('0')
        self.calculated_discount_amount = Decimal('0')
        self.tags = ['From Re-platform', ]
        self.payment_method = None
        self.shipping_address = None

    @classmethod
    def from_cart(cls, cart: 'Cart') -> 'Order':
        PaymentMethod = apps.get_model('billing', 'PaymentMethod')
        """
        This is a convenience method that allows the developer to create an order
        given a `Cart` object.
        """
        cart_line_items = cart.line_items.filter()
        number_of_servings = cart_line_items.aggregate(Sum('quantity')).get('quantity__sum')
        customer_discount = cart.customer.discounts.filter(
            customer_child=cart.customer_child,
            is_active=True,
        ).order_by('-applied_at').first()
        address = cart.customer.addresses.first()
        payment_method = PaymentMethod.objects.filter(
            customer=cart.customer,
            is_valid=True,
            setup_for_future_charges=True,
        ).order_by('-created_at').first()
        builder = cls()\
            .set_customer(cart.customer)\
            .set_customer_child(cart.customer_child)\
            .set_number_of_servings(number_of_servings)\
            .set_shipping_rate(None)\
            .set_shipping_address(address)\
            .add_line_items([item for item in cart_line_items])\
            .set_payment_method(payment_method)

        if customer_discount:
            builder.set_customer_discount(customer_discount)
        return builder.build().order

    @classmethod
    def from_subscription(cls, subscription: 'CustomerSubscription'):
        cart = subscription.customer_child.cart
        return cls.from_cart(cart)

    def set_customer(self, customer: 'Customer'):
        self.customer = customer
        return self

    def set_customer_child(self, customer_child: 'CustomerChild'):
        self.customer_child = customer_child
        return self

    def set_number_of_servings(self, number_of_servings: int):
        self.number_of_servings = number_of_servings
        return self

    def set_payment_method(self, payment_method: 'PaymentMethod'):
        self.payment_method = payment_method
        return self

    def set_shipping_rate(self, shipping_rate: 'ShippingRate' = None):
        if shipping_rate:
            self.shipping_rate = shipping_rate
        else:
            ShippingRate = apps.get_model('orders', 'ShippingRate')
            self.shipping_rate = ShippingRate.objects.filter(is_default=True).first()
        return self

    def set_shipping_address(self, address: 'Location'):
        self.shipping_address = address
        return self

    def add_line_item(self, line_item: 'CartLineItem'):
        self.line_items.append(line_item)
        return self

    def add_line_items(self, line_items: List):
        self.line_items.extend(line_items)
        return self

    def set_tax_amount(self, tax_amount: Decimal):
        self.tax_amount = tax_amount
        return self

    def add_tag(self, tag: str):
        self.tags.append(tag)
        return self

    def set_customer_discount(self, customer_discount: 'CustomerDiscount'):
        if not customer_discount:
            return self

        if customer_discount.is_active:
            self.customer_discount = customer_discount
            self.discount_amount = self.customer_discount.discount.amount
        return self

    def _create_order(self):
        Order = apps.get_model('orders', 'Order')
        ShippingRate = apps.get_model('orders', 'ShippingRate')
        try:
            self.order = Order(
                customer=self.customer,
                customer_child=self.customer_child,
                tax_total=self.tax_amount,
                payment_method=self.payment_method,
                shipping_rate=self.shipping_rate,
                shipping_address=self.shipping_address,
                applied_discount=self.customer_discount,
                tags=self.tags,
            )
            if self.shipping_rate:
                self.order.shipping_rate = self.shipping_rate
                self.order.save()
            else:
                self.order.shipping_rate = ShippingRate.objects.filter(is_default=True).first()
                self.order.save()
        except Exception as e:
            raise CannotBuildOrderError(e)

    def _clear_order(self):
        if self.order:
            Order = apps.get_model('orders', 'Order')
            self.order.line_items.filter().delete()
            Order.objects.filter(id=self.order.id).delete()

    def _create_line_items(self):
        OrderLineItem = apps.get_model('orders', 'OrderLineItem')

        try:
            _line_items = [
                OrderLineItem(
                    order=self.order,
                    product=line_item.product,
                    product_variant=line_item.product_variant,
                    quantity=line_item.quantity
                ) for line_item in self.line_items
            ]
            OrderLineItem.objects.bulk_create(_line_items)
        except Exception as e:
            raise CannotBuildOrderError(e)

    def build(self):
        if not self.customer:
            raise CannotBuildOrderError('A customer object is required to build an order')

        if not self.number_of_servings:
            raise CannotBuildOrderError('A number of servings (12,24) is required to build an order')

        if not self.payment_method:
            raise CannotBuildOrderError('Must set a payment method. Ensure the customer has a valid payment method')

        if not self.shipping_address:
            raise CannotBuildOrderError('An address is required to build an order')

        try:
            self._create_order()
        except CannotBuildOrderError:
            raise

        try:
            self._create_line_items()
        except CannotBuildOrderError:
            self._clear_order()
            raise

        calculator = PaymentCalculator.from_order(self.order)
        self.order.amount_total = calculator.amount_total
        self.order.subtotal_amount = calculator.subtotal_amount
        self.order.discount_amount_total = calculator.discount_total_amount
        self.order.save()

        return self
