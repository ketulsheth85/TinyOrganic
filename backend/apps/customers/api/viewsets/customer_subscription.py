import uuid

from django.conf import settings
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from sentry_sdk.utils import logger

from apps.carts.models import Cart, CartLineItem
from apps.customers.api.serializers import (
    CustomerSubscriptionReadOnlySerializer,
    CustomerSubscriptionWriteSerializer,
)
from apps.customers.models import Customer, CustomerChild, CustomerSubscription
from libs.brightback_client import BrightBackClient, CannotCreateBrightBackSessionURL


class CustomerSubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Contains the api endpoints for CRUD actions on customers subscriptions.

    This viewset adds a few optimizations based on
    https://hakibenita.com/django-rest-framework-slow#read-only-modelserializer
    """

    queryset = CustomerSubscription.objects.filter()
    serializer_class = CustomerSubscriptionReadOnlySerializer

    def get_serializer_class(self):
        """
        Retrieves the serializer class based on the action being taken on the `CustomerSubscription`.
        This is a way to optimize serialization times for customer objects.
        """
        if self.request.method in {'POST', 'PUT', 'PATCH'}:
            return CustomerSubscriptionWriteSerializer

        return self.serializer_class

    def create(self, request, *args, **kwargs):
        """
        Creates a new instance of `CustomerSubscription`.

        If the customer/child id combination is found in our database, then we will update it and
        send that result to the frontend. If the cart number_of_servings is less than the number
        current number of servings, we will clear out the corresponding cart
        """
        data = request.data
        customer_id = data.get('customer')
        customer_child_id = data.get('customer_child')
        number_of_servings = data.get('number_of_servings')
        frequency = data.get('frequency')
        customer = Customer.objects.get(id=customer_id)
        customer_child = CustomerChild.objects.get(id=customer_child_id)
        response_status = status.HTTP_200_OK

        try:
            subscription = CustomerSubscription.objects.get(
                customer=customer,
                customer_child=customer_child
            )

            subscription.number_of_servings = number_of_servings
            subscription.frequency = frequency
            subscription.save()

        except CustomerSubscription.DoesNotExist:
            subscription = CustomerSubscription.objects.create(
                customer=customer,
                customer_child=customer_child,
                frequency=frequency,
                number_of_servings=number_of_servings
            )
            response_status = status.HTTP_201_CREATED
        subscription.refresh_from_db()
        serializer = self.get_serializer_class()
        return Response(serializer(subscription).data, status=response_status)

    def _clear_customer_child_cart(self, customer, customer_child):
        cart = Cart.objects.get(
            customer=customer, customer_child=customer_child)
        line_items = CartLineItem.objects.filter(cart=cart)

        for line_item in line_items:
            item = CartLineItem.objects.filter(id=line_item.id)
            item.delete()

    def _create_cancellation_session(self):
        self.request.session['brightback_session_id'] = str(uuid.uuid4())
        return self.request.session['brightback_session_id']

    @action(methods=['GET'], detail=True)
    def precancel(self, request, *args, **kwargs):
        response_body = {}
        response_status = status.HTTP_200_OK
        if not settings.BRIGHTBACK_CANCELLATION_ENABLED:
            response_status = status.HTTP_404_NOT_FOUND
        else:
            subscription = self.get_object()
            if not subscription.is_active:
                response_body = {
                    "detail": "Cannot deactivate inactive subscription"}
                response_status = status.HTTP_400_BAD_REQUEST
            else:
                try:
                    self._create_cancellation_session()
                    cancellation_flow_client = BrightBackClient(
                        subscription, request.session['brightback_session_id']
                    )
                    url = cancellation_flow_client.get_cancellation_url()
                    response_body = {'url': url}
                except (CannotCreateBrightBackSessionURL, Exception) as e:
                    logger.error(e)
                    response_status = status.HTTP_400_BAD_REQUEST

        return Response(response_body, status=response_status)

    @action(methods=['PUT'], detail=True)
    def cancel(self, request, *args, **kwargs):
        subscription = self.get_object()
        subscription.deactivate()
        subscription.save()
        return Response(self.serializer_class(subscription).data, status=status.HTTP_200_OK)

    @action(methods=['PUT'], detail=True)
    def reactivate(self, request, *args, **kwargs):
        subscription = self.get_object()
        subscription.activate(create_order=True)
        subscription.save()
        return Response(self.serializer_class(subscription).data, status=status.HTTP_200_OK)
