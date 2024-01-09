from rest_framework import serializers

from apps.orders.models import ShippingRate


class ShippingRateReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingRate
        fields = 'id', 'price', 'title',
        read_only_fields = fields
