# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.auth.models                import Permission
from openbook.core.middleware.current_language import get_current_language

def perm_name_for_permission(permission: "Permission") -> str:
    """Get the translated permission display name from a permission object."""
    from .models.permission_text import PermissionText
    language = get_current_language()

    if not permission:
        return ""

    if language:
        try:
            translation = PermissionText.objects.get(parent = permission, language = language)

            if translation.name:
                return translation.name
        except PermissionText.DoesNotExist:
            pass

    return permission.name

def perm_string_for_permission(permission: "Permission") -> str:
    """Serialize a permission object to the Django permission string.

    The format is ``{app_label}.{codename}``.
    """
    return f"{permission.content_type.app_label}.{permission.codename}" if permission else ""

def app_label_for_permission(permission: "Permission") -> str:
    """Get the app label from a permission object."""
    return permission.content_type.app_label if permission else ""

def app_name_for_permission(permission: "Permission") -> str:
    """Get the translated app name from a permission object."""
    if not permission:
        return ""

    model = permission.content_type.model_class()
    return model._meta.app_config.verbose_name or permission.content_type.app_label

def model_for_permission(permission: "Permission") -> str:
    """Get the model label from a permission object."""
    if not permission:
        return ""

    return permission.content_type.model

def model_name_for_permission(permission: "Permission") -> str:
    """Get the translated model name from a permission object."""
    if not permission:
        return ""

    model = permission.content_type.model_class()

    if not model:
        return ""

    return model._meta.verbose_name

def permission_for_perm_string(perm: str) -> "Permission":
    """Get a permission object for a permission string.

    Raise ``Permission.DoesNotExist`` when the permission cannot be found.
    """
    if not perm:
        return None

    app_label, codename = perm.split(".", 1)
    return Permission.objects.get(codename=codename, content_type__app_label=app_label)

