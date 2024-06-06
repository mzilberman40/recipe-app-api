"""
Tests for models
"""
from unittest.mock import patch

from my_utils import log_call
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        log_call()

        email = "test@example.com"
        password = "Password_123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized dor new users."""
        log_call()

        simple_emails = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['TeSt2@EXAMPLE.COM', 'TeSt2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in simple_emails:
            user = get_user_model().objects.create_user(email=email, password="123GJGuyg")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating user without an email creating ValueError"""
        log_call()

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="", password="123GJGuyg")

    def test_create_superuser(self):
        """Test that creating superuser"""
        log_call()

        user = get_user_model().objects.create_superuser(email="ass@ASS.RU", password="123GJGuyg")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful """
        log_call()

        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="Password_123"
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description"
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful """
        log_call()

        user = get_user_model().objects.create_user(email="test@example.com", password="Password_123")
        tag = models.Tag.objects.create(user=user, name="Tag1")
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating a ingredient is successful """
        log_call()

        user = get_user_model().objects.create_user(email="test@example.com", password="Password_123")
        ingredient = models.Ingredient.objects.create(user=user, name="Salt")
        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path"""
        uuid = 'test_uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
