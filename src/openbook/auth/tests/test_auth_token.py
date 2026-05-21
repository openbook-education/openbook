# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.test               import TestCase
from django.urls               import reverse

from openbook.test             import ModelViewSetTestMixin
from ..middleware.current_user import reset_current_user
from ..models.auth_token       import AuthToken
from ..models.user             import User
from ..utils                   import permission_for_perm_string

class AuthToken_ViewSet_Tests(ModelViewSetTestMixin, TestCase):
    """Test the AuthTokenViewSet REST API."""
    base_name         = "auth_token"
    model             = AuthToken
    search_string     = "user1"
    search_count      = 2
    sort_field        = "token"
    expandable_fields = ["user"]

    def setUp(self):
        super().setUp()
        reset_current_user()

        self.user1    = User.objects.create_user("user1", password="password", email="user1@test.com")
        self.token1_1 = AuthToken.objects.create(user=self.user1, name="User 1 Token 1")
        self.token1_2 = AuthToken.objects.create(user=self.user1, name="User 1 Token 2")

        self.user2    = User.objects.create_user("user2", password="password", email="user2@test.com")
        self.token2_1 = AuthToken.objects.create(user=self.user2, name="User 2 Token 1")

        self.url_list         = reverse("auth_token-list")
        self.url_token1_1     = reverse("auth_token-detail", args=(self.token1_1.id,))
        self.url_current_user = reverse("current_user-list")

        permissions = (
            permission_for_perm_string("openbook_auth.manage_own_authtoken"),
        )

        self.user1.user_permissions.set(permissions)
        self.user2.user_permissions.set(permissions)

    def pk_found(self):
        return self.token1_1.id

    operations = {
        "create": {
            "request_data": {
                "user": "user1",
                "name": "Create Token",
            },
            "username":         "user1",
            "password":         "password",

            # Don't add default "add_authtoken" permission, because that would allow
            # to add tokens for any user. Not needed since the test user already has
            # "manage_own_authtoken" permission.
            "model_permission": "",
        },
        "update": {
            "request_data": {
                "name":        "New Name",
                "description": "New Description",
                "text_format": "HTML",
                "is_active":   True,
                "start_date":  "",
                "end_date":    "",
            },
            "updates": {
                "name":        "New Name",
                "description": "New Description",
                "text_format": "HTML",
                "is_active":   True,
                "start_date":  None,
                "end_date":    None,
            }
        },
        "partial_update": {
            "request_data": {"is_active": False},
            "updates":      {"is_active": False},
        },
    }

    def test_only_own_tokens(self):
        """Ensure users can access only their own tokens."""
        self.login("user1", "password")
        response = self.client.get(self.url_list)

        expected = AuthToken.objects.filter(user=self.user1).count()
        self.assertEqual(response.data["count"], expected)

        for token in response.data["results"]:
            self.assertEqual(token["user"], "user1")

    def test_create_other_user_forbidden(self):
        """Ensure users cannot create tokens for other users."""
        self.login("user1", "password")

        response = self.client.post(self.url_list, {
            "user": "user1",
            "name": "Same user",
        })

        self.assertStatusCode(response, 201)    # Created

        response = self.client.post(self.url_list, {
            "user": "user2",
            "name": "Other user",
        })

        self.assertStatusCode(response, 404)    # Not Found

    def test_change_user_forbidden(self):
        """Ensure users cannot change the token owner."""
        self.login("user1", "password")

        response = self.client.put(self.url_token1_1, {
            "user": "user2",
            "name": "Other user",
        })

        self.assertEqual(response.data["user"], "user1")

    def test_token_authentication_invalid_token(self):
        """Ensure authentication with an invalid token fails."""
        response = self.client.get(self.url_current_user, headers={
            "Authorization": "Token NOT-FOUND"
        })

        self.assertStatusCode(response, 403)

    def test_token_authentication_valid_token(self):
        """Ensure authentication with a valid token succeeds."""
        response = self.client.get(self.url_current_user, headers={
            "Authorization": f"Token {self.token1_1.token}"
        })

        self.assertStatusCode(response, 200)
        self.assertEqual(response.data["username"], "user1")
