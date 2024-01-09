from rest_framework import routers

from apps.billing.api.viewsets import PaymentIntentViewSet, ChargeViewSet, PaymentMethodViewSet

billing_router = routers.DefaultRouter()
billing_router.register('charge', ChargeViewSet)
billing_router.register('payment-method', PaymentMethodViewSet, basename='payment-method')
#stripe specific routes
billing_router.register('payment-intent', PaymentIntentViewSet, basename='payment-intent')
