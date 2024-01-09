import uuid

import analytics
from django.conf import settings
from django.contrib.auth import authenticate, logout, login
from django.db import transaction
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.customers.api.serializers import CustomerReadOnlySerializer, CustomerWriteSerializer
from apps.customers.models import Customer
from apps.customers.models import CustomerChild

from apps.customers.api.serializers.customer_child import (
    CustomerChildReadOnlySerializer,
    CustomerChildWriteSerializer,
)

class CustomerViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Contains the api endpoints for CRUD actions on customers.

    This viewset adds a few optimizations based on 
    https://hakibenita.com/django-rest-framework-slow#read-only-modelserializer
    """

    queryset = Customer.objects.filter()
    serializer_class = CustomerReadOnlySerializer

    def get_serializer_class(self):
        """
        Retrieves the serializer class based on the action being taken on the `Customer`. This is a way to optimize
        serialization times for customer objects.
        """
        if self.request.method in {'POST', 'PUT', 'PATCH'}:
            return CustomerWriteSerializer

        return self.serializer_class

    def create(self, request, *args, **kwargs):
        """
        Creates a new instance of `Customer`.

        If the customer's email is found in our database, then we will fetch the customer record
        and return a 200 status response. The frontend should check the status response code and 
        re-direct the customer to the step in which they left off in their previous session.

        """
        data = request.data
        response_status = status.HTTP_201_CREATED

        temp_password = str(uuid.uuid4())
        try:
            with transaction.atomic():
                try:
                    customer = Customer.objects.get(
                        email=data.get('email').lower(),
                        status='lead',
                    )
                    # if Customer.objects.get(email=data.get("email")):
                    return Response("User already exists", status=status.HTTP_400_BAD_REQUEST)
                    # customer.set_password(temp_password)
                    # customer.save()
                    # response_status = status.HTTP_200_OK
                except Customer.DoesNotExist:
                    customer = Customer.objects.create_user(
                        email=data.get('email').lower(),
                        first_name="",
                        last_name="",
                        password=temp_password
                    )
                    print("customer",customer.id)
                    customer_child=CustomerChild.objects.create(
                        parent=customer,
                        first_name=data.get('child_name').lower(),
                        birth_date=data.get('dob').lower(),
                        allergy_severity=data.get('allergy_severity').lower()
                        )
                    if data.get('allergy_severity').lower()!="none":
                        customer_child.allergies.set(data.get('allergies'))
                        customer_child.save()
                    print("child",customer_child)
            customer.refresh_from_db()
            cus_serializer = self.get_serializer_class()
            customer_data = cus_serializer(customer).data
            if request.user and request.user.is_authenticated:
                logout(request)

            customer = authenticate(request, username=customer.email, password=temp_password)
            if customer:
                login(request, customer)
            else:
                raise Exception("Could not log user in", customer.password)
            return Response({"message":"Created Successfully","data":customer_data}, status=response_status)
        except Exception as e:
            return Response({"message":"Please check the data!!","data":str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        password = request.data.get('password')

        # This will invalidate current session
        user.set_password(password)
        user.save()

        # reauthenticate user once password is set
        customer = authenticate(request, username=user.email, password=password)
        login(request, customer)

        return Response({'status': 'password set'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def current_user(self, request, pk=None):
        customer = request.user

        if customer and customer.is_authenticated:
            serializer = self.get_serializer_class()
            customer_data = serializer(customer).data

            return Response(customer_data, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_200_OK)
