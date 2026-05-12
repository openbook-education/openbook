# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.core.exceptions                import ValidationError
from django.db.utils                       import IntegrityError
from django.test                           import TestCase

from openbook.core.utils.content_type      import model_string_for_content_type
from openbook.content.models.course        import Course
from openbook.content.models.library_group import LibraryGroup
from openbook.test                         import ModelViewSetTestMixin
from ..middleware.current_user             import reset_current_user
from ..models.role                         import Role
from ..models.role_assignment              import RoleAssignment
from ..models.user                         import User

class RoleAssignment_Test_Mixin:
    def setUp(self):
        super().setUp()
        reset_current_user()

        self.user            = User.objects.create_user(username="test-new", email="test-new@example.com", password="password")
        self.library_group   = LibraryGroup.objects.create(name="Test", slug="test")
        self.course          = Course.objects.create(name="Test Course", slug="test-course", group=self.library_group)
        self.role_student    = Role.from_obj(self.course, name="Student", slug="student", priority=0)
        self.role_assistant  = Role.from_obj(self.course, name="Assistant", slug="assistant", priority=1)
        self.role_teacher    = Role.from_obj(self.course, name="Teacher", slug="teacher", priority=2)

        self.role_student.save()
        self.role_assistant.save()
        self.role_teacher.save()

class RoleAssignment_Model_Tests(RoleAssignment_Test_Mixin):
    """Test the RoleAssignment model.

    Methods enroll() and withdraw() require an enrollment method or access
    request as the first parameter. They are therefore already tested in unit
    tests for those models.
    """
    def test_role_scope(self):
        """Ensure the assigned role belongs to the same scope."""
        wrong_scope = Course.objects.create(name="Other Course", slug="other-course", group=self.library_group)
        wrong_role  = Role.from_obj(wrong_scope, name="Wrong Scope", slug="wrong-scope", priority=0)
        wrong_role.save()

        role_assignment = RoleAssignment.from_obj(self.course, user=self.user, role=wrong_role)

        with self.assertRaises(ValidationError):
            role_assignment.clean()

    def test_cannot_assign_twice(self):
        """Ensure the same role cannot be assigned to the same user twice."""
        RoleAssignment.from_obj(self.course, user=self.user, role=self.role_student).save()

        with self.assertRaises(IntegrityError):
            RoleAssignment.from_obj(self.course, user=self.user, role=self.role_student).save()

class RoleAssignment_ViewSet_Tests(ModelViewSetTestMixin, RoleAssignment_Test_Mixin, TestCase):
    """Test the RoleAssignmentViewSet REST API."""
    base_name         = "role_assignment"
    model             = RoleAssignment
    search_string     = "test-new"
    search_count      = 2
    sort_field        = "user"
    expandable_fields = ["user", "role", "enrollment_method", "access_request", "created_by", "modified_by"]

    def setUp(self):
        super().setUp()

        self.ra_student = RoleAssignment.from_obj(self.course, role=self.role_student, user=self.user)
        self.ra_student.save()

        self.ra_assistant = RoleAssignment.from_obj(self.course, role=self.role_assistant, user=self.user)
        self.ra_assistant.save()

    def pk_found(self):
        return self.ra_student.id

    def get_create_request_data(self):
        return {
            "scope_type": model_string_for_content_type(self.ra_student.scope_type),
            "scope_uuid": str(self.ra_student.scope_uuid),
            "role":       "teacher",
            "user":       "test-new",
        }

    def get_update_request_data(self):
        return {
                "scope_type": model_string_for_content_type(self.ra_student.scope_type),
                "scope_uuid": str(self.ra_student.scope_uuid),
                "role":       "teacher",
                "user":       "test-new",
                "is_active":  False,
                "start_date": "",
                "end_date":   "",
            }

    operations = {
        "create": {
            "request_data": get_create_request_data,
        },
        "update": {
            "request_data": get_update_request_data,
            "updates": {
                "role":       {"slug": "teacher"},
                "user":       {"username": "test-new"},
                "is_active":  False,
                "start_date": None,
                "end_date":   None,
            }
        },
        "partial_update": {
            "request_data": {"is_active": False},
            "updates":      {"is_active": False},
        },
    }
