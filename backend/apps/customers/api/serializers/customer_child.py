from rest_framework import serializers

from apps.customers.models import CustomerChild
from apps.recipes.models import Ingredient
from apps.recipes.api.serializers import IngredientReadOnlySerializer


class CustomerChildReadOnlySerializer(serializers.ModelSerializer):
    allergies = serializers.SerializerMethodField()

    class Meta:
        model = CustomerChild
        fields = 'id', 'parent', 'first_name', 'birth_date', 'sex', 'allergies', 'allergy_severity',
        read_only_fields = fields

    def get_allergies(self, obj):
        return [IngredientReadOnlySerializer(allergy).data for allergy in obj.allergies.filter()]


class CustomerChildWriteSerializer(CustomerChildReadOnlySerializer):
    allergies = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.filter(), many=True, required=False)
    class Meta(CustomerChildReadOnlySerializer.Meta):
        read_only_fields = 'id',
