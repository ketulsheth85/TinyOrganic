from rest_framework import mixins, viewsets

from apps.orders.api.serializers.shipping_rate import ShippingRateReadOnlySerializer
from apps.orders.models import ShippingRate


class ShippingRateViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ShippingRate.objects.filter(is_active=True)
    serializer_class = ShippingRateReadOnlySerializer
