from rest_framework import serializers

from apps.discounts.models import Discount, CustomerDiscount


class DiscountReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = 'id', 'codename', 'is_active', 'is_primary', 'banner_text', 'from_yotpo'


class CustomerDiscountReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDiscount
        fields = 'id', 'discount',
