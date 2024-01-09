from rest_framework import serializers

from apps.carts.models import Cart


class CartReadOnlySerializer(serializers.ModelSerializer):
    line_items = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    child = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = 'id', 'customer', 'child', 'line_items',
        read_only_fields = fields

    def get_line_items(self, obj):
        if obj:
            from apps.carts.api.serializers import CartLineItemReadOnlySerializer
            return [CartLineItemReadOnlySerializer(instance=line_item).data for line_item in obj.line_items.filter()]
        return []

    def get_customer(self, obj):
        return obj.customer_id if obj else ''

    def get_child(self, obj):
        return obj.customer_child_id if obj else ''


class CartWriteSerializer(CartReadOnlySerializer):
    class Meta(CartReadOnlySerializer.Meta):
        read_only_fields = 'id', 'customer', 'child',
