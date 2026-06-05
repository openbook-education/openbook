# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.test                           import TestCase

from openbook.core.utils.content_type      import content_type_for_model_string
from openbook.core.utils.content_type      import model_string_for_content_type
from openbook.content.models.course        import Course
from openbook.content.models.library_group import LibraryGroup
from openbook.test                         import ModelViewSetTestMixin
from ..middleware.current_user             import reset_current_user
from ..models.access_request               import AccessRequest
from ..models.allowed_role_permission      import AllowedRolePermission
from ..models.enrollment_method            import EnrollmentMethod
from ..models.role                         import Role
from ..models.role_assignment              import RoleAssignment
from ..models.user                         import User
from ..utils                               import permission_for_perm_string

class Role_ViewSet_Tests(ModelViewSetTestMixin, TestCase):
    """Test the RoleViewSet REST API."""
    base_name         = "role"
    model             = Role
    search_string     = "teacher"
    search_count      = 1
    sort_field        = "name"
    expandable_fields = ["permissions[]", "created_by", "modified_by", "role_assignments[]", "enrollment_methods[]", "access_requests[]"]

    def setUp(self):
        super().setUp()
        reset_current_user()

        self.library_group  = LibraryGroup.objects.create(name="Test", slug="test")
        self.course         = Course.objects.create(name="Test Course", slug="test-course", group=self.library_group)
        self.role_student   = Role.from_obj(self.course, name="Student", slug="student", priority=0)
        self.role_assistant = Role.from_obj(self.course, name="Assistant", slug="assistant", priority=1)
        self.role_teacher   = Role.from_obj(self.course, name="Teacher", slug="teacher", priority=2)

        self.role_student.save()
        self.role_assistant.save()
        self.role_teacher.save()

        scope_type = content_type_for_model_string("openbook_content.course")
        AllowedRolePermission.objects.create(scope_type=scope_type, permission=permission_for_perm_string("admin.add_logentry"))
        AllowedRolePermission.objects.create(scope_type=scope_type, permission=permission_for_perm_string("admin.change_logentry"))
        AllowedRolePermission.objects.create(scope_type=scope_type, permission=permission_for_perm_string("admin.delete_logentry"))
        AllowedRolePermission.objects.create(scope_type=scope_type, permission=permission_for_perm_string("admin.view_logentry"))

        # For testing the expandable fields
        self.role_student.permissions.set([
            permission_for_perm_string("admin.view_logentry")
        ])

        user_student1 = User.objects.create_user("student1", password="password", email="student1@test.com")
        RoleAssignment.from_obj(self.course, role=self.role_student, user=user_student1).save()

        user_student2 = User.objects.create_user("student2", password="password", email="student2@test.com")
        AccessRequest.from_obj(self.course, role=self.role_student, user=user_student2).save()

        EnrollmentMethod.from_obj(self.course, name="test", role=self.role_student, passphrase="test!").save()

    def pk_found(self):
        return self.role_student.id

    def get_create_request_data(self):
        return {
            "scope_type":  model_string_for_content_type(self.role_student.scope_type),
            "scope_uuid":  str(self.role_student.scope_uuid),
            "priority":    3,
            "name":        "Course Administrator",
            "slug":        "course-administrator",
            "permissions": ["admin.add_logentry", "admin.change_logentry"],
        }

    def get_update_request_data(self):
        return {
            "scope_type":  model_string_for_content_type(self.role_student.scope_type),
            "scope_uuid":  str(self.role_student.scope_uuid),
            "priority":    99,
            "name":        "Updated Name",
            "slug":        "updated-name",
            "description": "Updated Description",
            "is_active":   False,
            "permissions": ["admin.delete_logentry", "admin.view_logentry"],
        }

    operations = {
        "create": {
            "request_data": get_create_request_data,
        },
        "update": {
            "request_data": get_update_request_data,
            "updates": {
                "name":               "Updated Name",
                "slug":               "updated-name",
                "description":        "Updated Description",
                "is_active":          False,
                "permissions": [
                    {"codename": "delete_logentry"},
                    {"codename": "view_logentry"},
                ],
            }
        },
        "partial_update": {
            "request_data": {"is_active": False},
            "updates":      {"is_active": False},
        },
    }
