from decimal import Decimal

from django.apps import apps
from django.db.models import Sum
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from apps.addresses.models import Location
from apps.billing.models import PaymentMethod
from apps.carts.models import Cart
from apps.customers.models import CustomerSubscription
from apps.discounts.libs import DiscountBuilder, CannotCreateDiscountForCustomerError
from apps.orders.api.serializers import OrderReadOnlySerializer
from apps.orders.libs import (
    CannotBuildOrderError,
    OrderBuilder,
    OrderSummaryDetailDTO,
    OrderPaymentStatusEnum,
    PaymentCalculator,
)
from apps.discounts.models import Discount, CustomerDiscount
from apps.orders.models import Order, ShippingRate
from libs.tax_nexus.avalara import TaxProcessorClient
from libs.tax_nexus.avalara.client import CouldNotCalculateTaxForPurchaseError


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.filter().prefetch_related('customer')
    serializer_class = OrderReadOnlySerializer
    tax_client = TaxProcessorClient()

    def get_queryset(self):
        return super().get_queryset().filter(
            customer_id=self.request.query_params.get('customer'),
        )

    def create(self, request, *args, **kwargs):
        data = request.data
        customer_id = data.get('customer', None)
        if not customer_id:
            raise CannotBuildOrderError('Request payload requires a customer id')
        cart_ids = data.get('carts')
        carts = Cart.objects.filter(
            id__in=cart_ids,
            customer_child__is_deleted=False,
        ).prefetch_related('customer', 'line_items')
        payment_method = PaymentMethod.objects.filter(
            customer_id=customer_id,
        ).first()

        serialized_orders = []
        for cart in carts:
            customer_discount = CustomerDiscount.objects.filter(
                customer_child=cart.customer_child,
                is_active=True,
            ).first()
            number_of_servings = cart.line_items.aggregate(Sum('quantity')).get('quantity__sum')

            shipping_address = cart.customer.addresses.first()
            if not shipping_address.is_complete:
                raise CannotBuildOrderError('Address Information is required.')

            builder = OrderBuilder() \
                .set_customer(cart.customer) \
                .add_line_items([line_item for line_item in cart.line_items.filter()]) \
                .set_customer_child(cart.customer_child) \
                .set_number_of_servings(number_of_servings) \
                .set_shipping_rate(None)\
                .set_shipping_address(shipping_address)\
                .set_customer_discount(customer_discount)\
                .set_payment_method(payment_method)

            tax_calculation = self.tax_client \
                .set_customer_discount(customer_discount) \
                .set_shipping_rate(builder.shipping_rate) \
                .calculate_tax(cart)

            builder \
                .set_tax_amount(tax_calculation.get('total_tax')) \
                .build()

            order = builder.order
            order.tags = ['First Order Subscription', ]
            order.charge()
            order.save()

            serialized_orders.append(self.serializer_class(order).data)
            subscription, _ = CustomerSubscription.objects.get_or_create(
                customer_child=cart.customer_child,
                customer=order.customer,
                status='inactive',
            )
            subscription.activate(create_order=False)
            subscription.save()
            cart.customer.has_active_subscriptions = True
            cart.customer.status = 'subscriber'
            cart.customer.save()

            cart.remove_onetime_line_items()
            cart.save()

        return Response(serialized_orders, status=status.HTTP_201_CREATED)

    @action(methods=['GET', ], detail=False)
    def latest(self, request, **kwargs):
        customer = self.request.query_params.get('customer')
        customer_child = self.request.query_params.get('customer_child')
        if not request.user or not request.user.is_authenticated:
            return Response(
                'You are not authorized to access this endpoint. Please login',
                status=status.HTTP_403_FORBIDDEN
            )

        if not customer or not customer_child:
            raise APIException('The customer and child ID are required to retrieve')

        if request.user and request.user.is_authenticated:
            order = Order.objects.filter(
                customer=request.user,
                customer_child=customer_child,
            ).order_by('-created_at').first()

        response_data = {}
        if order:
            response_data = self.serializer_class(order).data

        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['GET', ], detail=False)
    def summary(self, request, **kwargs):
        customer_id = self.request.query_params.get('customer', None)

        if not customer_id:
            raise APIException('The customer ID is required to retrieve order summary')

        Customer = apps.get_model('customers', 'Customer')
        customer = Customer.objects.get(id=customer_id)

        children = customer.children.filter().prefetch_related('cart')
        discount_code = self.request.query_params.get('discount')
        running_summary = {
            "subtotal": Decimal('0'),
            "discounts": Decimal('0'),
            "shipping": Decimal('0'),
            "taxes": Decimal('0'),
            "total": Decimal('0')
        }
        if discount_code:
            discount = Discount.objects.filter(is_active=True, codename__iexact=discount_code).first()
            discount_builder = DiscountBuilder()\
                .set_discount(discount)\
                .set_customer(customer)

            for child in children:
                discount_builder.add_cart(child.cart)

            try:
                discount_builder.build()
            except CannotCreateDiscountForCustomerError as e:
                raise APIException(e)

        for child in children:
            customer_discount = CustomerDiscount.objects.filter(customer_child=child, is_active=True).first()
            default_shipping_rate = ShippingRate.objects.filter(is_default=True).first()
            summary_data = OrderSummaryDetailDTO(
                cart=child.cart,
                customer_discount=customer_discount,
                shipping_rate=default_shipping_rate,
            )

            try:
                tax_calculation = self.tax_client \
                    .set_customer_discount(customer_discount) \
                    .set_shipping_rate(summary_data.shipping_rate) \
                    .calculate_tax(child.cart)
                total_tax = tax_calculation.get('total_tax')
            # The first time a user requests a summary, they might not have an address
            except (Location.DoesNotExist, CouldNotCalculateTaxForPurchaseError):
                total_tax = Decimal(0)
            summary_data.tax_amount = total_tax

            summary = PaymentCalculator.summary(summary_data)

            running_summary['subtotal'] += summary['subtotal']
            running_summary['discounts'] += summary['discounts']
            running_summary['taxes'] += summary['taxes']
            running_summary['total'] += summary['total']
            running_summary['shipping'] += summary['shipping']

        return Response(running_summary, status=status.HTTP_200_OK)
