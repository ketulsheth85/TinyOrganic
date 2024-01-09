from rest_framework.routers import SimpleRouter

from apps.customers.api.viewsets import CustomerChildViewSet, CustomerViewSet, CustomerSubscriptionViewSet

customer_router = SimpleRouter()
customer_router.register('customers-subscriptions', CustomerSubscriptionViewSet, basename="customersubscription")
customer_router.register('customers-children', CustomerChildViewSet)
customer_router.register('customers', CustomerViewSet)
