# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.contrib.contenttypes.models import ContentType
from django.utils.translation           import gettext_lazy as _
from drf_spectacular.utils              import extend_schema_field
from rest_framework.serializers         import RelatedField
from uuid                               import UUID

from openbook.core.utils.content_type   import content_type_for_model_string
from ..models.role                      import Role

@extend_schema_field(str)
class RoleField(RelatedField):
    """Use role slugs instead of raw primary keys for input and output."""
    default_error_messages = {
        "not_found":           _("Role '{value}' not found."),
        "invalid-slug":        _("Invalid format: Expected a role slug."),
        "invalid-scope_type":  _("Invalid format: Expected scope type string"),
        "invalid-scope_uuid":  _("Invalid format: Expected scope UUID string"),
        "required-slug":       _("Role slug is required."),
        "required-scope":      _("Scope type and scope UUID are required."),
    }

    def get_queryset(self):
        if not self.read_only:
            return Role.objects.all()

    def to_internal_value(self, data):
        if data is None:
            if self.required:
                self.fail("required-slug")
            else:
                return None

        if not isinstance(data, str):
            self.fail("invalid-slug")

        if self.parent.instance:
            scope_type = self.parent.instance.scope_type
            scope_uuid = self.parent.instance.scope_uuid
        elif self.parent.initial_data:
            scope_type = self.parent.initial_data.get("scope_type", None)
            scope_uuid = self.parent.initial_data.get("scope_uuid", None)
        else:
            self.fail("required-scope")

        if scope_type is None or scope_uuid is None:
            if self.required:
                self.fail("required-scope")
            else:
                return None

        if not isinstance(scope_type, str) and not isinstance(scope_type, ContentType):
            self.fail("invalid-scope_type")
        if not isinstance(scope_uuid, str) and not isinstance(scope_uuid, UUID):
            self.fail("invalid-scope_uuid")

        if isinstance(scope_type, str):
            scope_type = content_type_for_model_string(scope_type)

        try:
            queryset = self.get_queryset()
            return queryset.get(scope_type=scope_type, scope_uuid=scope_uuid, slug=data)
        except Role.DoesNotExist:
            self.fail("not_found", value=data)

    def to_representation(self, obj):
        return obj.slug
