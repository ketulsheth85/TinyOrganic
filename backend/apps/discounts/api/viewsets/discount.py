import os
from decimal import Decimal

from django.apps import apps
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.carts.models import Cart
from apps.customers.models import Customer
from apps.discounts.api.serializers.discount import (
    CustomerDiscountReadOnlySerializer,
    DiscountReadOnlySerializer,
)
from apps.discounts.tasks import create_customer_referral_coupon_from_loyalty_client
from apps.discounts.libs import DiscountBuilder, CannotCreateDiscountForCustomerError
from apps.discounts.models import Discount, CustomerDiscount, CustomerDiscountStatusEnum
from libs import locking
from libs.yotpo_client import YotpoClient, CouldNotGetYotpoCustomerError


class DiscountViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Discount.objects.filter()
    serializer_class = DiscountReadOnlySerializer
    loyalty_client = YotpoClient()

    def get_queryset(self):
        q = super().get_queryset()
        filters = {
            'is_active': True
        }

        if self.request.query_params.get('primary'):
            filters['is_primary'] = True
        if self.request.query_params.get('codename'):
            filters['codename'] = self.request.query_params.get('codename')
        return q.filter(**filters)

    def _create_customer_coupon(self, customer):
        from_yotpo = True

        try:
            yotpo_customer = self.loyalty_client.get_customer(str(customer.id))
            discount_code = yotpo_customer.get('referral_code').get('code')
        except CouldNotGetYotpoCustomerError:
            from_yotpo = False
            create_customer_referral_coupon_from_loyalty_client.delay(customer.id)
            discount_code = os.urandom(7)

        discount = Discount.objects.create(
            codename=discount_code,
            referrer=customer,
            discount_type='fixed amount',
            amount=Decimal('30.00'),
            banner_text=f"Save $30 on your first order with {customer.first_name}'s referral code: {discount_code}",
            is_active=True,
            from_yotpo=from_yotpo
        )
        return discount

    def _get_customer_coupon(self, customer):
        Customer = apps.get_model('customers', 'Customer')

        customer = Customer.objects.get(id=customer.id)
        if customer.referral_discount_codes.filter().exists():
            discount = Discount.objects.filter(referrer=customer).last()
        else:
            discount = self._create_customer_coupon(customer)
        return discount

    @action(methods=['GET'], detail=False)
    def customer(self, request):
        customer = request.user
        if not customer:
            raise Exception('You must be logged in to get your discount code')

        customer_coupon = self._get_customer_coupon(customer)

        return Response(self.serializer_class(customer_coupon).data, status=status.HTTP_200_OK)


class CustomerDiscountViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = CustomerDiscount.objects.filter()
    serializer_class = CustomerDiscountReadOnlySerializer

    def _assert_valid_cancellation_payload(self, data):
        session_id = data.get('session')
        subscription_id = data.get('subscription')
        CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')
        with locking.acquire_shared_lock_context(f'subscription-cancellation-session-{subscription_id}', 'celery'):
            subscription = CustomerSubscription.objects.filter(
                id=subscription_id,
                customer=self.request.user,
                is_active=True
            ).first()
            if session_id != self.request.session['brightback_session_id']:
                raise CannotCreateDiscountForCustomerError('Customer is not eligible for this discount')
            if not subscription:
                raise CannotCreateDiscountForCustomerError('Cannot find customer subscription')
            if not subscription.is_active:
                raise CannotCreateDiscountForCustomerError('Customer Subscription is not active')

    def _end_cancellation_session(self):
        self.request.session['brightback_session_id'] = ''

    def create(self, request, *args, **kwargs):
        data = request.data
        customer = Customer.objects.get(id=data.get('customer'))
        try:
            discount = Discount.objects.get(codename__iexact=data.get('discount'))
        except Discount.DoesNotExist:
            return Response('Your discount code could not be found.', status=status.HTTP_404_NOT_FOUND)

        customer_discount = self.get_queryset().filter(
            discount=discount,
            customer_id=data.get('customer'),
            customer_child__in=[child for child in customer.children.filter()],
            status=CustomerDiscountStatusEnum.redeemed,
        )

        if customer_discount.exists():
            return Response('This coupon code has already been redeemed', status=status.HTTP_403_FORBIDDEN)

        if discount.from_brightback:
            self._assert_valid_cancellation_payload(data)

        discount_builder = DiscountBuilder()\
            .set_discount(discount)\
            .set_customer(customer)
        carts = Cart.objects.filter(customer=customer)
        for cart in carts:
            discount_builder.add_cart(cart)

        discount_builder.build()
        serialized_data = [
            self.serializer_class(customer_discount).data
            for customer_discount in discount_builder.customer_discounts
        ]

        # End user cancellation session after customer coupon has been applied
        if discount.from_brightback:
            self._end_cancellation_session()

        return Response(serialized_data, status=status.HTTP_200_OK)
