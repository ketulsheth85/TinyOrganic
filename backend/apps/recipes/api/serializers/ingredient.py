from rest_framework import serializers

from apps.recipes.models import Ingredient


class BaseIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = 'id', 'name'
        read_only_fields = fields


class IngredientReadOnlySerializer(BaseIngredientSerializer):
    name = serializers.SerializerMethodField()

    class Meta(BaseIngredientSerializer.Meta):
        ...

    def get_name(self, obj):
        return obj.name.lower()




class IngredientWriteSerializer(BaseIngredientSerializer):
    class Meta(BaseIngredientSerializer.Meta):
        read_only_fields = 'id',
