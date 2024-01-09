from rest_framework import viewsets

from apps.customers.models import CustomerSubscription
from apps.products.api.serializers import ProductReadOnlySerializer
from apps.products.models import Product


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Contains the api endpoints for Readonly actions on Products.
    """
    queryset = Product.objects.filter()
    serializer_class = ProductReadOnlySerializer

    def get_queryset(self):
        q = super().get_queryset()
        filters = {}
        # supported query args
        if self.request.query_params.get('product_type'):
            filters['product_type'] = self.request.query_params.get('product_type')
        if self.request.query_params.get('is_active'):
            filters['is_active'] = self.request.query_params.get('is_active') == 'true'
        if self.request.query_params.get('child'):
            subscription = CustomerSubscription.objects.get(customer_child_id=self.request.query_params.get('child'))
            filters['variants__sku_id__icontains'] = subscription.number_of_servings

        q = q.filter(**filters)
        
        return q
