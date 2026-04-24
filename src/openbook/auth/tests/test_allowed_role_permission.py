# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.core.exceptions           import ValidationError
from django.test                      import TestCase

from openbook.core.utils.content_type import content_type_for_model_string
from openbook.test                    import ModelViewSetTestMixin
from ..middleware.current_user        import reset_current_user
from ..models.allowed_role_permission import AllowedRolePermission
from ..utils                          import permission_for_perm_string
from ..validators                     import validate_permissions

class AllowedRolePermissionTextest_Mixin:
    def setUp(self):
        super().setUp()
        reset_current_user()
        
        self.scope_type = content_type_for_model_string("openbook_content.course")

        self.allowed_permission = AllowedRolePermission.objects.create(
            scope_type = self.scope_type,
            permission = permission_for_perm_string("admin.add_logentry"),
        )

        AllowedRolePermission.objects.create(
            scope_type = self.scope_type,
            permission = permission_for_perm_string("admin.view_logentry"),
        )

class AllowedRolePermission_Model_Tests(AllowedRolePermissionTextest_Mixin, TestCase):
    """
    Tests for the `AllowedRolePermission` model.
    """
    def test_validate_permissions(self):
        """
        Validation must only whitelisted permissions for roles or scopes.

        NOTE: Calling `add()` or `set()` on a relationship field automatically saves the relationship.
        Validation must therefore be handled by higher levels, which is why only the implementation of
        it is tested here.
        """
        allowed = [
            permission_for_perm_string("admin.add_logentry"),
            permission_for_perm_string("admin.view_logentry"),
        ]

        disallowed = [
            permission_for_perm_string("admin.change_logentry"),
        ]

        validate_permissions(self.scope_type, allowed)

        with self.assertRaises(ValidationError):
            validate_permissions(self.scope_type, disallowed)
    
class AllowedRolePermission_ViewSet_Tests(ModelViewSetTestMixin, AllowedRolePermissionTextest_Mixin, TestCase):
    """
    Tests for the `AllowedRolePermissionViewSet` REST API.
    """
    base_name         = "allowed_role_permission"
    model             = AllowedRolePermission
    search_string     = "add_logentry"
    search_count      = 1
    sort_field        = "permission"
    expandable_fields = ["permission"]

    operations = {
        "list":           {"requires_auth": False},
        "retrieve":       {"requires_auth": False},
        "create":         {"supported": False},
        "update":         {"supported": False},
        "partial_update": {"supported": False},
        "destroy":        {"supported": False},
    }

    def pk_found(self):
        return self.allowed_permission.id