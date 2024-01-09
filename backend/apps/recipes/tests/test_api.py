from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.recipes.tests.factories import IngredientFactory

#
# class IngredientAPITestCase(APITestCase):
#     @classmethod
#     def setUpTestData(cls) -> None:
#         cls.ingredients = [
#             IngredientFactory(name=ingredient_name)
#             for ingredient_name in ('ingredient1', 'ingredient2', 'ingredient3', 'ingredient4' , 'allergen1', 'allergen2')
#         ]
#
#     def test_will_display_allergens_when_found(self):
#         url = reverse('ingredient-list')
#
#         response = self.client.get(f'{url}?name=allergen')
#         self.assertEqual(len(response.json()), 2)
#
#     def test_will_not_display_allergens_when_not_found(self):
#         url = reverse('ingredient-list')
#
#         response = self.client.get(f'{url}?name=foo')
#         self.assertEqual(len(response.json()), 0)
#
#     def test_can_add_new_allergen(self):
#         url = reverse('ingredient-list')
#         response = self.client.post(url, data={'name': 'new_allergen'})
#         self.assertEqual(response.status_code, 201)
