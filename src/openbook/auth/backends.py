# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models   import AbstractUser

class RoleBasedObjectPermissionsBackend(ModelBackend):
    """
    Check object permissions with role-based fallbacks.

    For normal permission checks without an object, behave exactly like the stock
    model authentication backend. Check object permissions in the following order,
    stopping at the first match:

    1. The user is a superuser
    2. The user and the object are the same
    3. The user is the object's owner (optional).
    4. The object's has_obj_perm() method (optional).
    5. Regular non-object permissions

    Superusers can do anything. Users can change their own data. The owner is always authorized.
    Otherwise role-based permissions are checked. If this is not supported by the object or fails,
    fall back to regular user permissions. Thus, the ModelBackend does not need to be included
    in the Django settings, as its function is already covered here.
    """
    def has_perm(self, user_obj: AbstractUser, perm: str, obj=None) -> bool:
        # Superuser can do anything
        if user_obj.is_superuser:
            return True

        result = False

        # Anonymous permission always apply
        from openbook.auth.models import AnonymousPermission
        from openbook.auth.utils  import permission_for_perm_string

        try:
            AnonymousPermission.objects.get(permission=permission_for_perm_string(perm))
            return True
        except AnonymousPermission.DoesNotExist:
            pass

        # Check object permissions
        if obj is not None:
            if obj == user_obj:
                result = True
            if hasattr(obj, "owner") and obj.owner == user_obj:
                result = True
            elif hasattr(obj, "has_obj_perm"):
                result = obj.has_obj_perm(user_obj, perm)

        # Fallback to regular permission check
        if not result:
            result = super().has_perm(user_obj, perm)

        # Fallback to "change" permission when "view" fails
        if not result and ".view_" in perm:
            change_perm = perm.replace(".view_", ".change_")
            result = self.has_perm(user_obj, change_perm, obj)

        return result
