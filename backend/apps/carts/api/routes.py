from rest_framework.routers import SimpleRouter

from apps.carts.api.viewsets import CartViewSet

carts_router = SimpleRouter()
carts_router.register('carts', CartViewSet)
