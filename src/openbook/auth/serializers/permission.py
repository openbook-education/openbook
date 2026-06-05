# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.auth.models import Permission
from django.utils.translation   import gettext_lazy as _
from drf_spectacular.utils      import extend_schema_field
from rest_framework.serializers import RelatedField

from ..utils                    import perm_string_for_permission
from ..utils                    import permission_for_perm_string

@extend_schema_field(str)
class PermissionField(RelatedField):
    """Use permission strings instead of raw primary keys for input and output."""
    default_error_messages = {
        "not_found": _("Permission '{value}' not found."),
        "invalid":   _("Invalid format: Expected a permission string."),
        "required":  _("Permission string is required."),
    }

    def get_queryset(self):
        if not self.read_only:
            return Permission.objects.all()

    def to_internal_value(self, data):
        if data is None:
            if self.required:
                self.fail("required")
            else:
                return None

        if not isinstance(data, str):
            self.fail("invalid")

        try:
            return permission_for_perm_string(data)
        except Permission.DoesNotExist:
            self.fail("not_found", value=data)

    def to_representation(self, obj):
        return perm_string_for_permission(obj)
