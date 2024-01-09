from rest_framework.routers import SimpleRouter

from apps.orders.api.viewsets import OrderViewSet
from apps.orders.api.viewsets.shipping_rate import ShippingRateViewSet

orders_router = SimpleRouter()
orders_router.register('orders', OrderViewSet)
orders_router.register('shipping_rates', ShippingRateViewSet)
