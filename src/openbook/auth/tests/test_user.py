# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.core.exceptions    import ValidationError
from django.test               import TestCase
from django.urls               import reverse

from openbook.test             import ModelViewSetTestMixin
from ..middleware.current_user import reset_current_user
from ..models.user             import User

class User_Model_Tests(TestCase):
    """Test the User model."""
    def test_user_creation_without_email(self):
        """Ensure creating a user without an email fails validation."""
        # Directly saving without validation works
        User.objects.create_user("test1", password="test1234")

        # Model validation should raise an exception
        with self.assertRaises(ValidationError):
            user = User(username="test2", password="test1234")
            user.full_clean()
            user.save()

class User_ViewSet_Test(ModelViewSetTestMixin, TestCase):
    """Test the UserViewSet REST API."""
    base_name     = "user"
    model         = User
    pk_field      = "username"
    pk_found      = "user1"
    search_string = "unknown-user"
    search_count  = 0
    sort_field    = "username"

    operations = {
        "create": {
            "supported": False,
        },
        "update": {
            "request_data": {
                "first_name": "Changed First Name",
                "last_name":  "Changed Last Name",
                "description": "Changed Description",
            },
            "updates": {
                "first_name": "Changed First Name",
                "last_name":  "Changed Last Name",
                "description": "Changed Description",
            },

            # Use pre-configured user with correct permissions
            "username":         "user1",
            "password":         "password",
            "model_permission": (),
            "format":           "json",
            "content_type":     None,
        },
        "partial_update": {
            "request_data": {"first_name": "Changed First Name"},
            "updates":      {"first_name": "Changed First Name"},

            # Use pre-configured user with correct permissions
            "username":         "admin",
            "password":         "password",
            "model_permission": (),
        },
        "destroy": {
            # Use pre-configured user with correct permissions
            "username":         "user1",
            "password":         "password",
            "model_permission": (),
        }
    }

    def setUp(self):
        super().setUp()
        reset_current_user()

        self.user1 = User.objects.create_user("user1", password="password", email="user1@test.com")
        self.user2 = User.objects.create_user("user2", password="password", email="user2@test.com")
        self.user3 = User.objects.create_user("user3", password="password", email="user3@test.com")
        self.admin = User.objects.create_user("admin", password="password", email="admin@test.com", is_staff=True, is_superuser=True)

        self.url_user2 = reverse("user-detail", args=[str(self.user2.username)])

    def test_update_other_user_forbidden(self):
        """Ensure PUT cannot update another user."""
        self.login(username="user1", password="password")

        response = self.client.put(self.url_user2, {
            "password":        "password",
            "email":           "user2@test.com",
            "description":     "Updated",
            "profile_picture": "",
        })

        self.assertEqual(response.status_code, 404)

    def test_partial_update_other_user_forbidden(self):
        """Ensure PATCH cannot partially update another user."""
        self.login(username="user1", password="password")
        response = self.client.patch(self.url_user2, {"description": "Changed Description"}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_delete_other_user_forbidden(self):
        """Ensure DELETE cannot remove another user."""
        self.login(username="user1", password="password")
        response = self.client.delete(self.url_user2)
        self.assertEqual(response.status_code, 404)
