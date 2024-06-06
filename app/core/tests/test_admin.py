"""
Tests for django_admin modifications
"""
from my_utils import log_call
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Tests for django admin"""

    def setUp(self):
        """Create user and client"""
        self.client = Client()

        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='pass_secret123'
        )

        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='pass_secret123',
            name='Test User'
        )

        self.client.force_login(self.admin_user)

    def test_users_list(self):
        """ Test that users are listed on page"""
        log_call()

        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """ Test that edit user page works"""
        log_call()

        url = reverse('admin:core_user_change', args=[self.user.id])
        # print(url)
        res = self.client.get(url)
        # print(res)
        self.assertEqual(res.status_code, 200)

    def test_add_user_page(self):
        """ Test that add user page works"""
        log_call()

        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
