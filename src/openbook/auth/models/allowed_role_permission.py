# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib                       import admin
from django.contrib.auth.models           import Permission
from django.db                            import models
from django.contrib.contenttypes.models   import ContentType
from django.utils.translation             import gettext_lazy as _

from openbook.core.models.mixins.uuid     import UUIDMixin
from ..utils                              import perm_name_for_permission
from ..utils                              import perm_string_for_permission

class AllowedRolePermission(UUIDMixin):
    """
    Store permissions that can be used in scoped roles.

    This is used to restrict the list of available permissions when defining roles.
    """
    scope_type = models.ForeignKey(ContentType, verbose_name=_("Scope Type"), on_delete=models.CASCADE, related_name="+")
    permission = models.ForeignKey(Permission, verbose_name=_("Permission"), on_delete=models.CASCADE, related_name="+")

    class Meta:
        verbose_name        = _("Allowed Role Permission")
        verbose_name_plural = _("Allowed Role Permissions")

        indexes = [
            models.Index(fields=("scope_type",)),
        ]

        constraints = [
            models.UniqueConstraint(fields=("scope_type", "permission",), name="unique_allowed_role_permission"),
        ]

    def __str__(self):
        scope_name = f"{self.scope_type.name} |" if self.scope_type else ""
        perm_name  = f"{self.permission}" if self.permission else ""
        return f"{scope_name} {perm_name}".strip()

    @classmethod
    def get_for_scope_type(cls, scope_type: ContentType) -> "list[AllowedRolePermission]":
        """
        Return the allowed permissions for the given scope type.
        """
        return cls.objects.filter(scope_type=scope_type)

    @admin.display(description=_("Permission"))
    def perm_name(self, obj=None):
        return perm_name_for_permission(self.permission)

    @admin.display(description=_("Code"))
    def perm(self, obj=None):
        return perm_string_for_permission(self.permission)
