from rest_framework import serializers

from apps.carts.models import CartLineItem
from apps.products.api.serializers import ProductReadOnlySerializer
from apps.products.api.serializers.product import ProductVariantReadOnlySerializer
from apps.products.models import Product


class CartLineItemReadOnlySerializer(serializers.ModelSerializer):
    product = ProductReadOnlySerializer()
    product_variant = ProductVariantReadOnlySerializer()

    class Meta:
        model = CartLineItem
        fields = 'id', 'product', 'quantity', 'product_variant',
        read_only_fields = fields


class CartLineItemWriteSerializer(CartLineItemReadOnlySerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter())

    class Meta(CartLineItemReadOnlySerializer.Meta):
        read_only_fields = 'id',
