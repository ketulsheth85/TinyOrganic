from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from apps.products.models import Product, ProductVariant


class ProductReadOnlySerializer(serializers.ModelSerializer):
    ingredients = SerializerMethodField()
    variants = SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'description',
            'image_url',
            'price',
            'ingredients',
            'featured_ingredients',
            'product_type',
            'nutrition_image_url',
            'tags',
            'variants',
            'show_variants',
        )
        read_only_fields = fields

    def get_ingredients(self, obj):
        from apps.recipes.api.serializers.ingredient import IngredientReadOnlySerializer
        return [IngredientReadOnlySerializer(obj.ingredient).data for obj.ingredient in obj.ingredients.filter()]

    def get_variants(self, obj):
        return [ProductVariantReadOnlySerializer(variant).data for variant in obj.variants.filter()]

    def get_variants(self, obj):
        return [ProductVariantReadOnlySerializer(variant).data for variant in obj.variants.filter()]


class ProductVariantReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = 'id', 'price', 'sku_id', 'title'
