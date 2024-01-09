from django.db import transaction
from django.db.utils import IntegrityError
from django.http import JsonResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.addresses.api.serializers.location import (
    LocationReadOnlySerializer,
    LocationWriteSerializer,
)
from libs.tax_nexus.avalara.client import TaxProcessorClient
from apps.addresses.models import Location


class LocationChildViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.filter().select_related('customer')
    serializer_class = LocationReadOnlySerializer
    tax_client = TaxProcessorClient()

    def get_serializer_class(self):
        if self.request.method in {'POST', 'PUT', 'PATCH'}:
            return LocationWriteSerializer
        
        return LocationReadOnlySerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        data = serializer.data

        address_to_validate = serializer.create_instance()
        address_validation_payload = self.tax_client.validate_tax_address(address_to_validate)
        data['valid_address'] = address_validation_payload.get('valid_address')
        data['messages'] = address_validation_payload.get('messages')
        return Response(data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        instance.refresh_from_db()
        data = self.serializer_class(instance).data

        address_to_validate = serializer.create_instance()
        address_validation_payload = self.tax_client.validate_tax_address(address_to_validate)
        data['valid_address'] = address_validation_payload.get('valid_address')
        data['messages'] = address_validation_payload.get('messages')

        return Response(data)


