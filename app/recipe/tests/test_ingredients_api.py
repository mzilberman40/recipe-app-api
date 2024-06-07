"""Tests for ingredient API"""

from my_utils import log_call

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email="user1@example.com", password="Password_123"):
    """Create and return new user."""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(ingredient_id):
    """Create and return ingredient detail URL"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        log_call()
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user('user@example.com', 'test_pass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients"""
        log_call()
        Ingredient.objects.create(user=self.user, name="Salt")
        Ingredient.objects.create(user=self.user, name="Pepper")

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_list_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user"""
        log_call()

        user2 = create_user('user2@example.com', 'test_pass123')
        ingredient = Ingredient.objects.create(user=self.user, name="Pepper")
        Ingredient.objects.create(user=user2, name="butter")
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_ingredient_update(self):
        """Test updating an ingredient"""
        log_call()

        ingredient = Ingredient.objects.create(user=self.user, name="Cilantro")
        payload = {'name': 'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient"""
        log_call()
        ingredient = Ingredient.objects.create(user=self.user, name="Breakfast")
        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    #
    # def test_create_recipe(self):
    #     """Test creating a recipe"""
    #     log_call()
    #
    #     payload = {
    #         'title': 'Sample recipe',
    #         'time_minutes': 22,
    #         'price': Decimal('12.50'),
    #         'description': 'Sample description',
    #         'link': 'http://sample.com/recipe.pdf',
    #     }
    #     # print(payload)
    #     res = self.client.post(RECIPE_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #     recipe = Recipe.objects.get(id=res.data['id'])
    #     for k, v in payload.items():
    #         self.assertEqual(getattr(recipe, k), v)
    #     self.assertEqual(recipe.user, self.user)
    #

    #



    #
    # def test_update_user_returns_error(self):
    #     """Test changing the recipe user results in an error"""
    #     log_call()
    #     new_user = get_user_model().objects.create_user(
    #         'user2@example.com',
    #         'test_pass123'
    #     )
    #     recipe = create_recipe(user=self.user)
    #     payload = {
    #         'user': new_user,
    #     }
    #     url = detail_url(recipe.id)
    #     res = self.client.patch(url, payload)
    #     recipe.refresh_from_db()
    #     self.assertEqual(recipe.user, self.user)
    #

    #
    # def test_delete_other_user_recipe(self):
    #     """Test trying to delete another user's recipe"""
    #     log_call()
    #     other_user = get_user_model().objects.create_user('user2@example.com', 'test_pass123')
    #     recipe = create_recipe(user=other_user)
    #     url = detail_url(recipe.id)
    #     res = self.client.delete(url)
    #     self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
    #     self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
