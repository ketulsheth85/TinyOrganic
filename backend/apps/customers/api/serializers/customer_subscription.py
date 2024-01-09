from rest_framework import serializers

from apps.customers.models import CustomerSubscription


class CustomerSubscriptionReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSubscription
        fields = ('id', 'customer', 'customer_child', 'number_of_servings', 'frequency', 'is_active',
                  'activated_at', 'deactivated_at', 'status', 'next_order_charge_date')
        read_only_fields = fields


class CustomerSubscriptionWriteSerializer(CustomerSubscriptionReadOnlySerializer):
    class Meta(CustomerSubscriptionReadOnlySerializer.Meta):
        read_only_fields = 'id',
