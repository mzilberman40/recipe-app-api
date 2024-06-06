"""Tests for tag API"""
from my_utils import log_call

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def create_user(email="user1@example.com", password="Password_123"):
    """Create and return new user."""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(tag_id):
    """Create and return tag detail URL"""
    return reverse('recipe:tag-detail', args=[tag_id])


class PublicTagsAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        log_call()
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user('user@example.com', 'test_pass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags"""
        log_call()
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_list_limited_to_user(self):
        """Test list of tags is limited to authenticated user"""
        log_call()

        user2 = create_user('user2@example.com', 'test_pass123')
        tag = Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=user2, name="Dessert")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)


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


    def test_tag_update(self):
        """Test tag updating"""
        log_call()

        tag = Tag.objects.create(user=self.user, name="After Dinner")
        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag"""
        log_call()
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

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
