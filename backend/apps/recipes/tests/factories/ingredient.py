from factory import faker
from factory.django import DjangoModelFactory


class IngredientFactory(DjangoModelFactory):
    name = faker.Faker('name')

    class Meta:
        model = 'recipes.Ingredient'
