# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.conf                          import settings
from django.contrib.auth.models           import AbstractUser
from django.db                            import models
from django.utils.timezone                import now
from django.utils.translation             import gettext_lazy as _

from openbook.core.models.mixins.datetime import DurationMixin
from openbook.core.models.mixins.uuid     import UUIDMixin
from .mixins.audit                        import CreatedModifiedByMixin
from .mixins.scope                        import ScopeMixin

class AccessRequest(UUIDMixin, ScopeMixin, DurationMixin, CreatedModifiedByMixin):
    """
    Store access requests that users may send to the owners of a given scope.

    This contains the scope and requested role, so that the request can be converted into a role
    assignment if the request is granted.

    Note: Take care to exclude ``decision`` and ``decision_date`` when creating and modifying objects.
    """
    class Decision(models.TextChoices):
        PENDING  = "pending",  _("Decision Pending")
        ACCEPTED = "accepted", _("Accepted")
        DENIED   = "denied",   _("Denied")

    user          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="access_requests")
    role          = models.ForeignKey("Role", on_delete=models.CASCADE, related_name="access_requests")
    end_date      = models.DateTimeField(verbose_name=_("Enrollment Ends on"), blank=True, null=True)
    decision      = models.CharField(verbose_name=_("Decision"), max_length=10, choices=Decision, default=Decision.PENDING, null=False, blank=False)
    decision_date = models.DateTimeField(verbose_name=_("Decision Date"), blank=True, null=True)

    class Meta:
        verbose_name        = _("Access Request")
        verbose_name_plural = _("Access Requests")

        indexes = [
            models.Index(fields=("scope_type", "scope_uuid", "role")),
            models.Index(fields=("user",), name="user_idx"),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.role.name}"

    def has_obj_perm(self, user_obj: AbstractUser, perm: str) -> bool:
        """
        Allow viewing or deleting own access requests and creating new pending requests for the same user.

        Otherwise, use inherited object permission that the target role's priority must be lower or equal
        to any priority of the own assigned roles.
        """
        if self.user == user_obj:
            if ".delete_" in perm or ".view_" in perm:
                return True
            if ".add_" in perm and self.user == user_obj and self.decision == self.Decision.PENDING:
                return True

        return super().has_obj_perm(user_obj, perm)

    def save(self, *args, **kwargs):
        """
        Force pending decision when a new access request is saved. Also update the role assignments
        accordingly when a decision is made.
        """
        from .role_assignment import RoleAssignment

        if not self.decision:
            self.decision = self.Decision.PENDING

        if self.decision == self.Decision.PENDING:
            self.decision_date = None
        elif self.pk is not None:
            old = type(self).objects.get(pk=self.pk)

            if old.decision != self.decision:
                self.decision_date = now()

        permission_user = kwargs.pop("permission_user", None)
        check_permission = kwargs.pop("check_permission", True)

        match self.decision:
            case self.Decision.ACCEPTED:
                RoleAssignment.enroll(enrollment=self, permission_user=permission_user, check_permission=check_permission)
            case self.Decision.DENIED:
                RoleAssignment.withdraw(enrollment=self, permission_user=permission_user, check_permission=check_permission)

        super().save(*args, **kwargs)

    def accept(self,
        permission_user: AbstractUser = None,
        check_permission: bool = True
    ):
        """
        Accept request by setting the decision to accepted, saving the object and creating
        the role assignment.
        """
        self.decision      = self.Decision.ACCEPTED
        self.decision_date = now()
        self.save(permission_user=permission_user, check_permission=check_permission)

    def deny(self,
        permission_user: AbstractUser = None,
        check_permission: bool = True
    ):
        """
        Deny access request by setting the decision to denied and saving the object.
        """
        self.decision      = self.Decision.DENIED
        self.decision_date = now()
        self.save(permission_user=permission_user, check_permission=check_permission)
