# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from typing                             import Iterable

from django.contrib.auth.models         import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions             import ValidationError
from django.utils.translation           import gettext_lazy as _

from .models.allowed_role_permission    import AllowedRolePermission
from .models.mixins.scope               import ScopedRolesMixin

def validate_scope_type(scope_type: ContentType):
    """Check that the scope type model class implements ScopedRolesMixin."""
    if not issubclass(scope_type.model_class(), ScopedRolesMixin):
        raise ValidationError(_("Scope type %(scope_type)s is not valid."), params={
            "scope_type": scope_type.model_class()._meta.verbose_name
        })

def validate_permissions(scope_type: ContentType, permissions: Iterable[Permission]):
    """Check that only allowed permissions are assigned.

    Do nothing if either value is missing or only allowed permissions are used.
    Otherwise, raise ValidationError.
    """
    if not scope_type or not permissions:
        return

    allowed_permissions = [*AllowedRolePermission.get_for_scope_type(scope_type).values_list("permission", flat=True)]

    for permission in permissions:
        if not permission.pk in allowed_permissions:
            raise ValidationError(_("Permission %(perm)s cannot be assigned in this scope"), params={
                "perm": f"{permission}",
            })
