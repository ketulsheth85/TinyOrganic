from rest_framework import serializers

from apps.billing.models.charge import Charge


class ChargeReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        fields = 'id', 'customer', 'payment_method', 'payment_customer', 'amount',
        read_only_fields = fields


class ChargeWriteSerializer(ChargeReadOnlySerializer):
    class Meta(ChargeReadOnlySerializer.Meta):
        read_only_fields = 'id',
