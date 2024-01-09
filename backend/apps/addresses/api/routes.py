from rest_framework.routers import SimpleRouter

from apps.addresses.api.viewsets import LocationChildViewSet

addresses_router = SimpleRouter()
addresses_router.register('addresses', LocationChildViewSet)
