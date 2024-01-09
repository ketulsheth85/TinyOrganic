from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.customers.api.serializers.customer_child import (
    CustomerChildReadOnlySerializer,
    CustomerChildWriteSerializer,
)
from apps.customers.models import CustomerChild
from apps.products.libs import MealPlanRecommendationEngine


class CustomerChildViewSet(viewsets.ModelViewSet):
    queryset = CustomerChild.objects.filter().select_related('parent')
    serializer_class = CustomerChildReadOnlySerializer

    def get_serializer_class(self):
        if self.request.method in {'POST', 'PUT', 'PATCH'}:
            return CustomerChildWriteSerializer
        
        return CustomerChildReadOnlySerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        instance.refresh_from_db()
        return Response(self.serializer_class(instance).data)

    @action(methods=['GET'], detail=True)
    def recommended_products(self, request, *args, **kwargs):
        child = self.get_object()
        engine = MealPlanRecommendationEngine(child)
        engine.run()
        return Response(engine.recommendations)
