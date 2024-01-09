from rest_framework.routers import SimpleRouter

from apps.recipes.api.viewsets import IngredientViewSet

recipes_routes = SimpleRouter()
recipes_routes.register('ingredients', IngredientViewSet)
