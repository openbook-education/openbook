# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.core.exceptions                import PermissionDenied
from django.core.exceptions                import ValidationError
from django.urls                           import reverse
from django.test                           import TestCase
from unittest.mock                         import patch

from openbook.core.utils.content_type      import model_string_for_content_type
from openbook.content.models.course        import Course
from openbook.content.models.library_group import LibraryGroup
from openbook.test                         import ModelViewSetTestMixin
from ..middleware.current_user             import reset_current_user
from ..models.enrollment_method            import EnrollmentMethod
from ..models.role                         import Role
from ..models.role_assignment              import RoleAssignment
from ..models.user                         import User
from ..utils                               import permission_for_perm_string

class EnrollmentMethod_Test_Mixin:
    def setUp(self):
        super().setUp()
        reset_current_user()

        self.user          = User.objects.create_user(username="new", email="new@test.com", password="password")
        self.library_group = LibraryGroup.objects.create(name="Test", slug="test")
        self.course        = Course.objects.create(name="Test Course 1", slug="test-course1", group=self.library_group)

        self.course.public_permissions.add(
            permission_for_perm_string("openbook_auth.view_enrollmentmethod"),
            permission_for_perm_string("openbook_auth.self_enroll"),
        )

        self.role = Role.from_obj(self.course, name="Student", slug="student", priority=0)
        self.role.save()

        self.em_passphrase = EnrollmentMethod.from_obj(self.course, name="self-enrollment with passphrase", role=self.role, passphrase="Correct!")
        self.em_passphrase.save()

        self.em_no_passphrase = EnrollmentMethod.from_obj(self.course, name="self-enrollment", role=self.role)
        self.em_no_passphrase.save()

        self.course_no_self_enroll = Course.objects.create(name="Test Course 2", slug="test-course2", group=self.library_group)
        self.em_course_no_self_enroll = EnrollmentMethod.from_obj(self.course_no_self_enroll, name="self-enrollment", role=self.role)
        self.em_course_no_self_enroll.save()

class EnrollmentMethod_Model_Tests(EnrollmentMethod_Test_Mixin, TestCase):
    """Test the EnrollmentMethod model."""
    def test_role_scope(self):
        """Ensure the assigned role belongs to the same scope."""
        wrong_scope = Course.objects.create(name="Other Course", slug="other-course", group=self.library_group)
        wrong_role  = Role.from_obj(wrong_scope, name="Wrong Scope", slug="wrong-scope", priority=0)
        wrong_role.save()

        enrollment_method = EnrollmentMethod.from_obj(self.course, name="wrong-role", role=wrong_role)

        with self.assertRaises(ValidationError):
            enrollment_method.clean()

    def test_enroll_called(self):
        """Ensure RoleAssignment.enroll() is called on self-enrollment."""
        with patch.object(RoleAssignment, "enroll") as mock_enroll:
            self.em_no_passphrase.enroll(user=self.user, check_passphrase=False)

            mock_enroll.assert_called_once_with(
                enrollment       = self.em_no_passphrase,
                user             = self.user,
                passphrase       = None,
                check_passphrase = False,
                check_permission = False,
            )

    def test_return_role_assignment(self):
        """Ensure a RoleAssignment object is returned on self-enrollment."""
        result = self.em_no_passphrase.enroll(user=self.user, check_passphrase=False)
        self.assertIsInstance(result, RoleAssignment)

    def test_self_enrollment_disabled_permission_denied(self):
        """Ensure PermissionDenied is raised when self-enroll permission is missing."""
        with self.assertRaises(PermissionDenied):
            self.em_course_no_self_enroll.enroll(user=self.user)

    def test_wrong_passphrase_permission_denied(self):
        """Ensure PermissionDenied is raised when an invalid passphrase is used."""
        with self.assertRaises(PermissionDenied):
            self.em_passphrase.enroll(user=self.user, passphrase="Wrong!")

    def test_skip_passphrase_check(self):
        """Ensure wrong passphrases are ignored when check_passphrase is False."""
        self.em_passphrase.enroll(user=self.user, passphrase="Wrong!", check_passphrase=False)

    def test_correct_passphrase(self):
        """Ensure a correct passphrase creates a role assignment."""
        self.assertEqual(RoleAssignment.objects.filter(
            user = self.user,
            role = self.role,
        ).count(), 0)

        self.em_passphrase.enroll(user=self.user, passphrase="Correct!")

        self.assertEqual(RoleAssignment.objects.filter(
            user = self.user,
            role = self.role,
        ).count(), 1)

    def test_without_passphrase(self):
        """Ensure users can self-assign when no passphrase is required."""
        self.assertEqual(RoleAssignment.objects.filter(
            user = self.user,
            role = self.role,
        ).count(), 0)

        self.em_no_passphrase.enroll(user=self.user)

        self.assertEqual(RoleAssignment.objects.filter(
            user = self.user,
            role = self.role,
        ).count(), 1)

class EnrollmentMethod_ViewSet_Tests(ModelViewSetTestMixin, EnrollmentMethod_Test_Mixin, TestCase):
    """Test the EnrollmentMethodViewSet REST API."""
    base_name         = "enrollment_method"
    model             = EnrollmentMethod
    count             = 2       # Only the two from self.course are visible!
    search_string     = "passphrase"
    search_count      = 1
    sort_field        = "name"
    expandable_fields = ["role", "created_by", "modified_by"]

    def setUp(self):
        super().setUp()

        self.url_list                 = reverse("enrollment_method-list")
        self.url_no_passphrase_detail = reverse("enrollment_method-detail", args=[str(self.em_no_passphrase.pk)])
        self.url_no_passphrase_enroll = reverse("enrollment_method-enroll", args=[str(self.em_no_passphrase.pk)])
        self.url_passphrase_detail    = reverse("enrollment_method-detail", args=[str(self.em_passphrase.pk)])
        self.url_passphrase_enroll    = reverse("enrollment_method-enroll", args=[str(self.em_passphrase.pk)])
        self.url_no_self_enroll       = reverse("enrollment_method-enroll", args=[str(self.em_course_no_self_enroll.pk)])

    def pk_found(self):
        return self.em_passphrase.id

    def get_create_request_data(self):
        return {
            "scope_type": model_string_for_content_type(self.em_passphrase.scope_type),
            "scope_uuid": str(self.em_passphrase.scope_uuid),
            "name":       "Test Name",
            "role":       "student",
        }

    def get_update_request_data(self):
        return {
                "scope_type":      model_string_for_content_type(self.em_passphrase.scope_type),
                "scope_uuid":      str(self.em_passphrase.scope_uuid),
                "name":            "Changed Name",
                "description":     "Changed Description",
                "text_format":     EnrollmentMethod.TextFormatChoices.HTML,
                "role":            "student",
                "is_active":       False,
                "duration_value":  1,
                "duration_period": EnrollmentMethod.DurationPeriod.YEARS,
                "end_date":        "",
                "passphrase":      "TopSecret!",
            }

    operations = {
        # Cannot test list and retrieve with no permissions with this test data.
        # Since we need to have "openbook_auth.view_enrollmentmethod" in the test
        # courses public permissions, the permission check will always succeed.
        "list": {
            "model_permission": (),
        },
        "retrieve": {
            "model_permission": (),
        },

        "create": {
            "request_data": get_create_request_data,
        },
        "update": {
            "request_data": get_update_request_data,
            "updates": {
                "name":            "Changed Name",
                "description":     "Changed Description",
                "text_format":     EnrollmentMethod.TextFormatChoices.HTML,
                "role":            {"slug": "student"},
                "is_active":       False,
                "duration_value":  1,
                "duration_period": EnrollmentMethod.DurationPeriod.YEARS,
                "end_date":        None,
                "passphrase":      "TopSecret!",
            }
        },
        "partial_update": {
            "request_data": {"is_active": False},
            "updates":      {"is_active": False},
        },
    }

    def test_self_enrollment_no_passphrase(self):
        """Ensure self-enrollment works without a passphrase."""
        self.login(username="new", password="password")

        response = self.client.put(self.url_no_passphrase_enroll)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(RoleAssignment.objects.filter(
            user = self.user,
            role = self.role,
        ).count(), 1)

    def test_self_enrollment_correct_passphrase(self):
        """Ensure self-enrollment works with the correct passphrase."""
        self.login(username="new", password="password")

        response = self.client.put(self.url_passphrase_enroll, {"passphrase": "Correct!"})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(RoleAssignment.objects.filter(
            user = self.user,
            role = self.role,
        ).count(), 1)

    def test_self_enrollment_wrong_passphrase(self):
        """Ensure self-enrollment fails with a wrong passphrase."""
        self.login(username="new", password="password")

        response = self.client.put(self.url_passphrase_enroll, {"passphrase": "Wrong!"})
        self.assertEqual(response.status_code, 403)

        self.assertEqual(RoleAssignment.objects.filter(
            user = self.user,
            role = self.role,
        ).count(), 0)

    def test_self_enrollment_disabled_permission_denied(self):
        """Ensure enrollment returns denied when self-enroll permission is missing."""
        self.login(username="new", password="password")

        response = self.client.put(self.url_no_self_enroll)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(RoleAssignment.objects.filter(
            user = self.user,
            role = self.role,
        ).count(), 0)

    def test_self_enrollment_requires_auth(self):
        """Ensure self-enrollment fails when public permissions are not set."""
        self.login(username="new", password="password")

        self.course.public_permissions.set([])

        response = self.client.put(self.url_passphrase_enroll, {"passphrase": "Correct!"})
        self.assertEqual(response.status_code, 404)

        self.assertEqual(RoleAssignment.objects.filter(
            user = self.user,
            role = self.role,
        ).count(), 0)
