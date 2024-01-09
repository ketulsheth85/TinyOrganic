from rest_framework.routers import SimpleRouter

from apps.products.api.viewsets import ProductViewSet

product_router = SimpleRouter()
product_router.register('products', ProductViewSet)
