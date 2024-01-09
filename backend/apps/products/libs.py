from abc import abstractmethod
from dataclasses import dataclass

from dataclasses_json import dataclass_json
from django.apps import apps
from sentry_sdk.utils import logger
from django.conf import settings


class ProductTypeEnum:
    recipe = 'recipe'


@dataclass_json
@dataclass
class MealPlanRecipeDTO:
    product: 'Product'
    recipe_id: str
    title: str
    contains_allergen: bool


class BaseMealPlanRecommendationStrategy:
    def __init__(self, child: 'CustomerChild'):
        self.child = child
        self.recommendations = []

    @abstractmethod
    def execute(self):
        ...


class GetRecipesByZipcodeMixin:
    def get_recipes_by_zipcode(self):
        location = self.child.parent.addresses.filter()
        Product = apps.get_model('products', 'Product')
        query = {
            'product_type': ProductTypeEnum.recipe,
            'is_active': True,
        }

        # If we don't have a location, return all recipes
        if len(location):
            zipcode = location[0].zipcode
            FulfillmentCenterZipcode = apps.get_model('fulfillment', 'FulfillmentCenterZipcode')
            try:
                fulfillment_centers = {
                    warehouse.location for warehouse in FulfillmentCenterZipcode.objects
                    .get(zipcode=zipcode).warehouses.filter()
                }
                query['fulfillment_centers__location__in'] = fulfillment_centers
            except FulfillmentCenterZipcode.DoesNotExist as e:
                logger.error(e)
        return Product.objects.filter(**query).order_by('title')

    def get_recipes(self):
        if settings.FILTER_RECIPES_BY_ZIPCODE:
            return self.get_recipes_by_zipcode()

        Product = apps.get_model('products', 'Product')
        return Product.objects.filter(
            product_type=ProductTypeEnum.recipe,
            is_active=True,
        ).order_by('title')


class DisplayAllMealPlansRecommendationStrategy(BaseMealPlanRecommendationStrategy, GetRecipesByZipcodeMixin):
    def __init__(self, child: 'CustomerChild'):
        super().__init__(child)
        self.TINY_BEGINNINGS_MAX_CHILD_AGE_IN_MONTHS = 7
        self.TINY_BEGINNINGS_TAG_LIST = ['tiny-beginnings']

    def _get_child_cart_line_item_id_set(self):
        Cart = apps.get_model('carts', 'Cart')
        CartLineItem = apps.get_model('carts', 'CartLineItem')
        child_cart = Cart.objects.get(customer_child=self.child)
        child_cart_line_items = CartLineItem.objects.filter(cart=child_cart)
        return set([item.product.id for item in child_cart_line_items])

    def execute(self):
        from apps.products.api.serializers import ProductReadOnlySerializer

        child_cart_product_id_set = self._get_child_cart_line_item_id_set()
        for recipe in self.get_recipes():

            recipe_ingredients_list = recipe.ingredients.filter().values_list('name', flat=True)
            allergens_found = False
            for allergy_name in recipe_ingredients_list:
                if self.child.allergies.filter(
                    name__icontains=allergy_name,
                ).exists():
                    allergens_found = True

            if allergens_found and recipe.id not in child_cart_product_id_set:
                continue
            self.recommendations.append(
                MealPlanRecipeDTO(
                    product=ProductReadOnlySerializer(recipe).data,
                    recipe_id=f'{recipe.id}',
                    title=recipe.title,
                    contains_allergen=allergens_found,
                ).to_dict()
            )

        recommendation_listings = {
            'tiny_beginnings': [],
            'recommendations': [],
            'remaining_products': [],
        }

        tiny_beginnings_set = set(self.TINY_BEGINNINGS_TAG_LIST)
        recommendation_listing_count = 0

        for idx, obj in enumerate(self.recommendations):
            if set(obj['product']['tags']).intersection(tiny_beginnings_set):
                recommendation_listings['tiny_beginnings'].append(obj)
            elif recommendation_listing_count >= 6:
                recommendation_listings['remaining_products'].append(obj)
            else:
                recommendation_listings['recommendations'].append(obj)
                recommendation_listing_count = recommendation_listing_count+1

        if self.child.age_in_months <= self.TINY_BEGINNINGS_MAX_CHILD_AGE_IN_MONTHS:
            recommendation_listings['recommendations'] = \
                recommendation_listings['tiny_beginnings'] + recommendation_listings['recommendations']
            recommendation_listings['tiny_beginnings'] = []

        return recommendation_listings


class MealPlanRecommendationEngine:
    def __init__(
            self,
            child: 'CustomerChild',
            strategy: BaseMealPlanRecommendationStrategy = DisplayAllMealPlansRecommendationStrategy
    ):
        self.child = child
        self.strategy = strategy
        self.recommendations = {}

    def run(self):
        _strategy = self.strategy(self.child)
        self.recommendations = _strategy.execute()
        return self
