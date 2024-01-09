from rest_framework.routers import DefaultRouter

from apps.discounts.api.viewsets import DiscountViewSet, CustomerDiscountViewSet

discounts_router = DefaultRouter()

discounts_router.register('discounts', DiscountViewSet)
discounts_router.register('customer_discounts', CustomerDiscountViewSet)
