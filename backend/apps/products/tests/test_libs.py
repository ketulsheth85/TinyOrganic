from django.test import TestCase
from django.utils import timezone

from apps.addresses.tests.factories.location import LocationFactory
from apps.carts.tests.factories import CartFactory, CartLineItemFactory
from apps.customers.tests.factories import CustomerChildFactory
from apps.fulfillment.tests.factories import FulfillmentCenterFactory, FulfillmentCenterZipcodeFactory
from apps.products.libs import MealPlanRecommendationEngine, BaseMealPlanRecommendationStrategy, \
    GetRecipesByZipcodeMixin
from apps.products.tests.factories import ProductFactory
from apps.recipes.tests.factories import IngredientFactory

#
# class BaseMealPlanRecommendationStrategyTestSuite(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.ingredient = IngredientFactory(name='Coconut')
#         cls.another_ingredients = IngredientFactory(name='Apple')
#         cls.allergen_ingredient = IngredientFactory(name='Allergy')
#         cls.child = CustomerChildFactory()
#         cls.cart = CartFactory(customer=cls.child.parent, customer_child=cls.child)
#
#     def setUp(self) -> None:
#         self.tiny_beginnings_recipe = ProductFactory(
#             title='Tiny beginnings recipe',
#             ingredients=[self.ingredient],
#             tags=['tiny-beginnings']
#         )
#         self.recipe = ProductFactory(
#             title='Some Recipe',
#             ingredients=[self.ingredient, self.allergen_ingredient, ]
#         )
#
#         self.recipes = [
#             ProductFactory(title=f'Recipe {i}', ingredients=[self.another_ingredients, ])
#             for i in range(10)
#         ]
#         for recipe in self.recipes:
#             ProductVariantFactory(product=recipe)
#
#         self.recipes.append(self.recipe)
#
#         engine = MealPlanRecommendationEngine(self.child)
#         engine.run()
#         self.recommendations = engine.recommendations
#
#     def test_algorithm_presents_meal_plans_with_all_active_recipes(self):
#         self.assertIn('recommendations', self.recommendations)
#
#     def test_algorithm_filters_out_recipe_with_allergen_from_cart(self):
#         child = CustomerChildFactory(allergies=[self.allergen_ingredient])
#         CartFactory(customer=child.parent, customer_child=child)
#         product_with_allergy = ProductFactory(ingredients=[self.allergen_ingredient])
#
#         engine = MealPlanRecommendationEngine(child)
#         engine.run()
#         engine_recipe_ids = set([
#             product['product']['id'] for product in
#             engine.recommendations['recommendations'] + engine.recommendations['remaining_products']
#         ])
#
#         self.assertTrue(str(product_with_allergy.id) not in engine_recipe_ids)
#
#     def test_algorithm_does_not_filter_out_recipe_with_allergen_in_child_cart(self):
#         child = CustomerChildFactory(allergies=[self.allergen_ingredient])
#         cart = CartFactory(customer=child.parent, customer_child=child)
#         product_with_allergy = ProductFactory(ingredients=[self.allergen_ingredient])
#         CartLineItemFactory(cart=cart, product=product_with_allergy)
#
#         engine = MealPlanRecommendationEngine(child)
#         engine.run()
#         engine_recipe_ids = set([
#             product['product']['id'] for product in
#             engine.recommendations['recommendations'] + engine.recommendations['remaining_products']
#         ])
#
#         self.assertTrue(str(product_with_allergy.id) in engine_recipe_ids)
#
#     def test_algorithm_returns_tiny_beginnings_separately_for_aged_out_children(self):
#         nine_months_ago = timezone.now().date() - timezone.timedelta(days=30*9)
#         customer_child = CustomerChildFactory(birth_date=nine_months_ago)
#         CartFactory(customer=customer_child.parent, customer_child=customer_child)
#         meal_plan_engine = MealPlanRecommendationEngine(customer_child)
#         meal_plan_engine.run()
#
#         recommendations_recipe_id_set = {
#             product['product']['id'] for product in meal_plan_engine.recommendations['recommendations']
#         }
#         remaining_products_recipe_id_set = {
#             product['product']['id'] for product in meal_plan_engine.recommendations['remaining_products']
#         }
#
#         self.assertTrue(meal_plan_engine.recommendations['tiny_beginnings'])
#         self.assertFalse(str(self.tiny_beginnings_recipe.id) in recommendations_recipe_id_set)
#         self.assertFalse(str(self.tiny_beginnings_recipe.id) in remaining_products_recipe_id_set)
#
#     def test_algorithm_returns_tiny_beginnings_for_children_within_age_group(self):
#         eight_months_ago = timezone.now().date() - timezone.timedelta(days=30*4)
#         child = CustomerChildFactory(birth_date=eight_months_ago)
#         CartFactory(customer=child.parent, customer_child=child)
#         engine = MealPlanRecommendationEngine(child)
#         engine.run()
#
#         recommendations_recipe_id_set = {
#             product['product']['id'] for product in engine.recommendations['recommendations']
#         }
#         remaining_products_recipe_id_set = {
#             product['product']['id'] for product in engine.recommendations['remaining_products']
#         }
#         self.assertFalse(engine.recommendations['tiny_beginnings'])
#         self.assertTrue(str(self.tiny_beginnings_recipe.id) in recommendations_recipe_id_set)
#         self.assertFalse(str(self.tiny_beginnings_recipe.id) in remaining_products_recipe_id_set)


class MockRecommendationAlgorithm(
    BaseMealPlanRecommendationStrategy,
    GetRecipesByZipcodeMixin
):
    def execute(self):
        return self.get_recipes_by_zipcode()


class GetRecipesByZipcodeMixinTestSuite(TestCase):

    def test_can_filter_recipes_by_zipcode(self):
        child = CustomerChildFactory()
        fulfillment_center = FulfillmentCenterFactory(location='wallace')
        zipcode = FulfillmentCenterZipcodeFactory(zipcode='33165')
        zipcode.warehouses.add(fulfillment_center)
        LocationFactory(customer=child.parent, zipcode='33165')
        recipe_title_set = set()
        for i in range(3):
            p = ProductFactory(title=f'cool-product-{i}')
            p.fulfillment_centers.add(fulfillment_center)
            recipe_title_set.add(p.title)

        recommendation_algorithm = MockRecommendationAlgorithm(child)

        for recipe in recommendation_algorithm.execute():
            self.assertTrue(recipe.title in recipe_title_set)

    def test_can_get_recipes_when_zipcode_is_not_in_db(self):
        child = CustomerChildFactory()
        fulfillment_center = FulfillmentCenterFactory(location='wallace')

        LocationFactory(customer=child.parent, zipcode='33199')
        recipe_title_set = set()
        for i in range(8):
            p = ProductFactory(title=f'cool-product-{i}')
            p.fulfillment_centers.add(fulfillment_center)
            recipe_title_set.add(p.title)

        recommendation_algorithm = MockRecommendationAlgorithm(child)

        for recipe in recommendation_algorithm.execute():
            self.assertTrue(recipe.title in recipe_title_set)

    def test_can_get_recipes_without_an_address(self):
        child = CustomerChildFactory()
        fulfillment_center = FulfillmentCenterFactory(location='wallace')
        recipe_title_set = set()
        for i in range(6):
            p = ProductFactory(title=f'sensible-product-{i}')
            p.fulfillment_centers.add(fulfillment_center)
            recipe_title_set.add(p.title)

        recommendation_algorithm = MockRecommendationAlgorithm(child)

        for recipe in recommendation_algorithm.execute():
            self.assertTrue(recipe.title in recipe_title_set)
