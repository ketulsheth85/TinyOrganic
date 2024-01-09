from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from apps.recipes.api.serializers.ingredient import (
    IngredientReadOnlySerializer,
    IngredientWriteSerializer,
)
from apps.recipes.models import Ingredient


class IngredientViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    serializer_class = IngredientReadOnlySerializer
    queryset = Ingredient.objects.filter()

    def get_queryset(self):
        q = super().get_queryset()

        if self.request.query_params.get('name', False):
            q = q.filter(name__icontains=self.request.query_params.get('name'))
        
        return q

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return self.serializer_class
        return IngredientWriteSerializer
