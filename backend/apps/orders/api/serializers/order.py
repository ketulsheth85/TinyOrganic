from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from apps.orders.api.serializers.order_line_item import OrderLineItemReadOnlySerializer
from apps.customers.api.serializers import CustomerReadOnlySerializer
from apps.orders.models import Order

ORDER_FIELDS = ['id', 'customer', 'customer_child', 'fulfillment_status', 'payment_status',
                'amount_total', 'charged_amount', 'refunded_amount', 'charged_at', 
                'external_order_id', 'tracking_number', 'order_number',]


class OrderReadOnlySerializer(serializers.ModelSerializer):
    customer = CustomerReadOnlySerializer(read_only=True)
    order_line_items = SerializerMethodField()

    class Meta:
        model = Order
        fields = ORDER_FIELDS + ['order_line_items', ]
        read_only_fields = fields

    def get_order_line_items(self, obj):
        return [OrderLineItemReadOnlySerializer(item).data for item in obj.line_items.filter()]
