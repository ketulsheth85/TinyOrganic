from apps.addresses.api.routes import addresses_router
from apps.billing.api.routes import billing_router
from apps.carts.api.routes import carts_router
from apps.customers.api.routes import customer_router
from apps.discounts.api.routes import discounts_router
from apps.orders.api.routes import orders_router
from apps.recipes.api.routes import recipes_routes
from apps.products.api.routes import product_router
from apps.webhooks.api.routes import webhook_router

urlpatterns = [] \
              + customer_router.urls \
              + recipes_routes.urls \
              + addresses_router.urls \
              + carts_router.urls \
              + discounts_router.urls \
              + billing_router.urls \
              + orders_router.urls \
              + product_router.urls \
              + webhook_router.urls
