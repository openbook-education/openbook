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
from django.utils.translation             import gettext_lazy as _

from openbook.core.models.mixins.uuid     import UUIDMixin
from ..utils                              import perm_name_for_permission
from ..utils                              import perm_string_for_permission

class AnonymousPermission(UUIDMixin):
    """
    Store permissions for anonymous (not logged-in) users.

    This is required for our implementation of object-based permissions, which by default fail for
    anonymous users. Note that these permissions are automatically valid for authenticated users, too.
    """
    permission = models.ForeignKey(
        to           =  Permission,
        verbose_name = _("Permission"),
        on_delete    = models.CASCADE,
        related_name = "+",
        null         = False,
        blank        = False
    )

    class Meta:
        verbose_name        = _("Anonymous Permission")
        verbose_name_plural = _("Anonymous Permissions")

        constraints = [
            models.UniqueConstraint(fields=("permission",), name="unique_anonymous_permission"),
        ]

    def __str__(self):
        return self.perm_name()

    @admin.display(description=_("Permission"))
    def perm_name(self, obj=None):
        return perm_name_for_permission(self.permission)

    @admin.display(description=_("Code"))
    def perm(self, obj=None):
        return perm_string_for_permission(self.permission)
