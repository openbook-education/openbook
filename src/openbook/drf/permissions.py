# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from rest_framework.permissions import DjangoObjectPermissions

class DjangoObjectPermissionsOnly(DjangoObjectPermissions):
    """
    Class `APIView`, which is a parent for `ModelViewSet` in Django REST Framework the method
    `check_permissions()` is called very early and later `check_object_permissions()`, too.
    Since `DjangoObjectPermissions` is a `DjangoModelPermissions` it implements both checks.
    But DRF raises an exception when either method returns `False`, thus inverting the logic
    in our own authentication backend. Also both classes don't check "view" permissions by default.

    This class replaces `DjangoObjectPermissions` with a version more in line with our own backend.
    """
    # Include "view" permission
    perms_map = {
        "GET":     ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD":    ["%(app_label)s.view_%(model_name)s"],
        "POST":    ["%(app_label)s.add_%(model_name)s"],
        "PUT":     ["%(app_label)s.change_%(model_name)s"],
        "PATCH":   ["%(app_label)s.change_%(model_name)s"],
        "DELETE":  ["%(app_label)s.delete_%(model_name)s"],
    }

    def has_permission(self, request, view):
        # Always True to avoid PermissionDenied.
        # Our authentication backend checks model-permissions as fallback, instead.
        return True
