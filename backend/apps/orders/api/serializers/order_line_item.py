import json

from django.apps import apps
from rest_framework import serializers

from apps.orders.models import OrderLineItem
from apps.products.api.serializers import ProductReadOnlySerializer
from apps.products.api.serializers.product import ProductVariantReadOnlySerializer


class OrderLineItemReadOnlySerializer(serializers.ModelSerializer):
    product = ProductReadOnlySerializer()
    product_variant = ProductVariantReadOnlySerializer()

    class Meta:
        model = OrderLineItem
        fields = ['id', 'quantity', 'product', 'product_variant']
        read_only_fields = fields
