# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.core.exceptions           import ValidationError
from django.core.exceptions           import PermissionDenied
from django.test                      import TestCase
from django.utils                     import timezone
from unittest.mock                    import patch
from rest_framework.reverse           import reverse

from openbook.core.utils.content_type import model_string_for_content_type
from openbook.content.models.course   import Course
from openbook.test                    import ModelViewSetTestMixin
from ..middleware.current_user        import reset_current_user
from ..models.access_request          import AccessRequest
from ..models.role                    import Role
from ..models.role_assignment         import RoleAssignment
from ..models.user                    import User
from ..utils                          import permission_for_perm_string

class AccessRequest_Test_Mixin:
    def setUp(self):
        super().setUp()
        reset_current_user()

        self.user_new       = User.objects.create_user(username="new", email="new@test.com", password="password")
        self.user_student   = User.objects.create_user(username="student", email="student@test.com", password="password")
        self.user_assistant = User.objects.create_user(username="assistant", email="assistant@test.com", password="password")
        self.user_owner     = User.objects.create_user(username="owner", email="owner@test.com", password="password")
        self.user_dummy     = User.objects.create_user(username="dummy", email="dummy@test.com", password="password")
        self.course         = Course.objects.create(name="Test Course", slug="test-course", text_format=Course.TextFormatChoices.MARKDOWN, owner=self.user_owner)
        self.role_student   = Role.from_obj(self.course, name="Student", slug="student", priority=0)
        self.role_assistant = Role.from_obj(self.course, name="Assistant", slug="assistant", priority=1)
        self.role_teacher   = Role.from_obj(self.course, name="Teacher", slug="teacher", priority=2)

        self.role_student.save()
        self.role_assistant.save()
        self.role_teacher.save()

        permissions = [
            permission_for_perm_string("openbook_auth.add_accessrequest"),
            permission_for_perm_string("openbook_auth.view_accessrequest"),
            permission_for_perm_string("openbook_auth.change_accessrequest"),
            permission_for_perm_string("openbook_auth.delete_accessrequest"),
            permission_for_perm_string("openbook_auth.add_roleassignment"),
            permission_for_perm_string("openbook_auth.delete_roleassignment"),
        ]

        self.role_assistant.permissions.set(permissions)
        self.role_teacher.permissions.set(permissions)

        self.user_new.user_permissions.set([
            permission_for_perm_string("openbook_auth.add_accessrequest"),
            permission_for_perm_string("openbook_auth.delete_accessrequest"),
        ])

        RoleAssignment.from_obj(self.course, user=self.user_student, role=self.role_student).save()
        RoleAssignment.from_obj(self.course, user=self.user_assistant, role=self.role_assistant).save()

class AccessRequest_Model_Tests(AccessRequest_Test_Mixin, TestCase):
    """Test the AccessRequest model."""
    def test_role_scope(self):
        """Ensure the assigned role belongs to the same scope."""
        wrong_scope = Course.objects.create(name="Other Course", slug="other-course", text_format=Course.TextFormatChoices.MARKDOWN)
        wrong_role  = Role.from_obj(wrong_scope, name="Wrong Scope", slug="wrong-scope", priority=0)
        wrong_role.save()

        access_request = AccessRequest.from_obj(self.course, user=self.user_new, role=wrong_role)

        with self.assertRaises(ValidationError):
            access_request.clean()

    def test_new_pending_decision(self):
        """Ensure decision is pending and decision_date is None for new requests."""
        access_request = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_student)
        access_request.save(check_permission=False)

        self.assertEqual(access_request.decision, AccessRequest.Decision.PENDING)
        self.assertIsNone(access_request.decision_date)

    def test_decision_date_automatically_set_on_accept(self):
        """Ensure decision_date is set when an access request is accepted."""
        access_request = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_student)
        access_request.save(check_permission=False)

        self.assertIsNone(access_request.decision_date)

        access_request.decision = AccessRequest.Decision.ACCEPTED
        access_request.save(check_permission=False)

        self.assertIsNotNone(access_request.decision_date)
        self.assertIsInstance(access_request.decision_date, timezone.datetime)

    def test_decision_date_automatically_set_on_deny(self):
        """Ensure decision_date is set when an access request is denied."""
        access_request = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_student)
        access_request.save(check_permission=False)

        self.assertIsNone(access_request.decision_date)

        access_request.decision = AccessRequest.Decision.DENIED
        access_request.save(check_permission=False)

        self.assertIsNotNone(access_request.decision_date)
        self.assertIsInstance(access_request.decision_date, timezone.datetime)

    def test_enroll_on_accept(self):
        """Ensure RoleAssignment.enroll() is called when a request is accepted."""
        with patch.object(RoleAssignment, "enroll") as mock_enroll:
            access_request = AccessRequest.from_obj(self.course,
                user     = self.user_new,
                role     = self.role_student,
                decision = AccessRequest.Decision.ACCEPTED
            )

            access_request.save(check_permission=False)
            mock_enroll.assert_called_once_with(enrollment=access_request, permission_user=None, check_permission=False)

    def test_withdraw_on_deny(self):
        """Ensure RoleAssignment.withdraw() is called when a request is denied."""
        with patch.object(RoleAssignment, "withdraw") as mock_withdraw:
            access_request = AccessRequest.from_obj(self.course,
                user     = self.user_new,
                role     = self.role_student,
                decision = AccessRequest.Decision.DENIED
            )

            access_request.save(check_permission=False)
            mock_withdraw.assert_called_once_with(enrollment=access_request, permission_user=None, check_permission=False)

    def test_role_assigned_on_accept(self):
        """Ensure a role is assigned when an access request is accepted."""
        access_request = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_student)
        access_request.save(check_permission=False)

        with self.assertRaises(RoleAssignment.DoesNotExist):
            RoleAssignment.objects.get(
                user = self.user_new,
                role = self.role_student,
            )

        access_request.accept(check_permission=False)

        self.assertEqual(RoleAssignment.objects.filter(
            user = self.user_new,
            role = self.role_student,
        ).count(), 1)

        self.assertEqual(access_request.decision, AccessRequest.Decision.ACCEPTED)

    def test_role_unassigned_on_deny(self):
        """Ensure role assignment is deleted when an access request is denied."""
        access_request = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_student)
        access_request.save(check_permission=False)

        with self.assertRaises(RoleAssignment.DoesNotExist):
            RoleAssignment.objects.get(
                user = self.user_new,
                role = self.role_student,
            )

        access_request.deny(check_permission=False)

        self.assertEqual(RoleAssignment.objects.filter(
            user = self.user_new,
            role = self.role_student,
        ).count(), 0)

        self.assertEqual(access_request.decision, AccessRequest.Decision.DENIED)

    def test_cannot_decide_higher_priority(self):
        """Ensure users cannot decide requests for roles above their priority."""
        access_request = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_teacher)
        access_request.save(check_permission=False)

        with self.assertRaises(PermissionDenied):
            access_request.accept(permission_user=self.user_assistant)

        with self.assertRaises(PermissionDenied):
            access_request.deny(permission_user=self.user_assistant)

    def test_can_decide_same_priority(self):
        """Ensure users can decide requests for roles at their own priority."""
        access_request = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_assistant)
        access_request.save(check_permission=False)

        access_request.accept(permission_user=self.user_assistant)
        access_request.deny(permission_user=self.user_assistant)

    def test_can_decide_lower_priority(self):
        """Ensure users can decide requests for roles below their own priority."""
        access_request = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_student)
        access_request.save(check_permission=False)

        access_request.accept(permission_user=self.user_assistant)
        access_request.deny(permission_user=self.user_assistant)

    def test_accept_permission(self):
        """Ensure accepting requests requires openbook_auth.add_roleassignment."""
        # First try without permission
        access_request1 = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_student)

        access_request2 = AccessRequest.from_obj(self.course,
            user     = self.user_new,
            role     = self.role_student,
            decision = AccessRequest.Decision.ACCEPTED,
        )

        with self.assertRaises(PermissionDenied):
            access_request1.accept(permission_user=self.user_student)

        with self.assertRaises(PermissionDenied):
            access_request2.save(permission_user=self.user_student)

        # Now add permission and retry
        self.role_student.permissions.set([
            permission_for_perm_string("openbook_auth.add_roleassignment"),
        ])

        access_request3 = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_student)
        access_request3.accept(permission_user=self.user_student)

        access_request4 = AccessRequest.from_obj(self.course,
            user     = self.user_new,
            role     = self.role_student,
            decision = AccessRequest.Decision.ACCEPTED,
        )

        access_request4.save(permission_user=self.user_student)

    def test_deny_permission(self):
        """Ensure denying requests requires openbook_auth.delete_roleassignment."""
        # First try without permission
        access_request1 = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_student)

        access_request2 = AccessRequest.from_obj(self.course,
            user     = self.user_new,
            role     = self.role_student,
            decision = AccessRequest.Decision.DENIED,
        )

        with self.assertRaises(PermissionDenied):
            access_request1.deny(permission_user=self.user_student)


        with self.assertRaises(PermissionDenied):
            access_request2.save(permission_user=self.user_student)

        # Now add permission and retry
        self.role_student.permissions.set([
            permission_for_perm_string("openbook_auth.delete_roleassignment"),
        ])

        access_request3 = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_student)
        access_request3.deny(permission_user=self.user_student)

        access_request4 = AccessRequest.from_obj(self.course,
            user     = self.user_new,
            role     = self.role_student,
            decision = AccessRequest.Decision.DENIED,
        )

        access_request4.save(permission_user=self.user_student)

class AccessRequest_ViewSet_Tests(ModelViewSetTestMixin, AccessRequest_Test_Mixin, TestCase):
    """Test the AccessRequestViewSet REST API."""
    base_name         = "access_request"
    model             = AccessRequest
    search_string     = "student"
    search_count      = 1
    sort_field        = "decision"
    expandable_fields = ["user", "role", "created_by", "modified_by"]

    def setUp(self):
        super().setUp()

        self.access_request = AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_student)
        self.access_request.save(check_permission=False)

        AccessRequest.from_obj(self.course, user=self.user_new, role=self.role_assistant).save(check_permission=False)

    def pk_found(self):
        return self.access_request.id

    def get_create_request_data(self):
        return {
            "scope_type": model_string_for_content_type(self.role_student.scope_type),
            "scope_uuid": str(self.role_student.scope_uuid),
            "role":       "student",
            "user":       "new",
        }

    def get_update_request_data(self):
        return {
            "scope_type": model_string_for_content_type(self.role_student.scope_type),
            "scope_uuid": str(self.role_student.scope_uuid),
            "role":       "student",
            "user":       "dummy",
            "decision":   AccessRequest.Decision.ACCEPTED,
        }

    operations = {
        "create": {
            "request_data": get_create_request_data,
        },
        "update": {
            "request_data": get_update_request_data,
            "updates":      {
                "user":     {"username": "dummy"},
                "decision": AccessRequest.Decision.ACCEPTED,
            },

            # Use pre-configured user with correct permissions
            "username":         "owner",
            "password":         "password",
            "model_permission": (),
        },
        "partial_update": {
            "request_data":     {"decision": AccessRequest.Decision.DENIED},
            "updates":          {"decision": AccessRequest.Decision.DENIED},

            # Use pre-configured user with correct permissions
            "username":         "owner",
            "password":         "password",
            "model_permission": (),
        },
    }

    def test_permission_denied(self):
        """Ensure operations without required permissions return 404."""
        self.login(username="student", password="password")

        # Try to accept without permission
        url = reverse("access_request-accept", args=[str(self.access_request.pk)])
        response = self.client.put(url)
        self.assertEqual(response.status_code, 404)

        # Try to deny without permission
        url = reverse("access_request-deny", args=[str(self.access_request.pk)])
        response = self.client.put(url)
        self.assertEqual(response.status_code, 404)

    def test_accept(self):
        """Ensure accept assigns the role when permitted."""
        self.login(username="assistant", password="password")

        url = reverse("access_request-accept", args=[str(self.access_request.pk)])
        response = self.client.put(url)
        self.assertEqual(response.status_code, 200)

        self.access_request.refresh_from_db()
        self.assertEqual(self.access_request.decision, AccessRequest.Decision.ACCEPTED)

    def test_deny(self):
        """Ensure deny unassigns the role when permitted."""
        self.login(username="assistant", password="password")

        url = reverse("access_request-deny", args=[str(self.access_request.pk)])
        response = self.client.put(url)

        self.assertEqual(response.status_code, 200)
        self.access_request.refresh_from_db()
        self.assertEqual(self.access_request.decision, AccessRequest.Decision.DENIED)
