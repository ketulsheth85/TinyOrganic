from rest_framework import serializers

from apps.billing.models.payment_method import PaymentMethod


class PaymentMethodReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = 'id', 'customer', 'last_four', 'expiration_date',
        read_only_fields = fields


class PaymentMethodWriteSerializer(PaymentMethodReadOnlySerializer):
    class Meta(PaymentMethodReadOnlySerializer.Meta):
        fields = 'id', 'customer', 'payment_method', 'payment_customer',
        read_only_fields = 'id',
