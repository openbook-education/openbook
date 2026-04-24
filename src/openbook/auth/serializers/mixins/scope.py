# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.utils.translation           import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils              import extend_schema_field
from rest_flex_fields2.serializers      import FlexFieldsModelSerializer
from rest_framework.serializers         import PrimaryKeyRelatedField
from rest_framework.serializers         import RelatedField

from openbook.core.utils.content_type   import content_type_for_model_string
from openbook.core.utils.content_type   import model_string_for_content_type
from ..user                             import UserField
from ..permission                       import PermissionField
from ...validators                      import validate_scope_type
from ...validators                      import validate_permissions

class ScopedRolesSerializerMixin(FlexFieldsModelSerializer):
    """
    Mixin class for model serializers whose models implement the `ScopedRolesMixin` and as such
    act as permission scope for user roles. Default serializer, that adds all scope fields.
    """
    owner              = UserField(read_only=True)
    public_permissions = PermissionField(many=True)
    role_assignments   = PrimaryKeyRelatedField(many=True, read_only=True)
    enrollment_methods = PrimaryKeyRelatedField(many=True, read_only=True)
    access_requests    = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        fields = (
            "owner", "public_permissions",
            "role_assignments", "enrollment_methods", "access_requests",
        )

        read_only_fields = ("role_assignments", "enrollment_methods", "access_requests")

        expandable_fields = {
            "public_permissions": ("openbook.auth.viewsets.permission.PermissionSerializer",              {"many": True}),
            "role_assignments":   ("openbook.auth.viewsets.role_assignment.RoleAssignmentSerializer",     {"many": True}),
            "enrollment_methods": ("openbook.auth.viewsets.enrollment_method.EnrollmentMethodSerializer", {"many": True}),
            "access_requests":    ("openbook.auth.viewsets.access_request.AccessRequestSerializer",       {"many": True}),
        }

    def validate(self, attributes):
        """
        Check that only allowed permissions are assigned.
        """
        scope_type = ContentType.objects.get_for_model(self.Meta.model)
        public_permissions = attributes.get("public_permissions", None)

        validate_permissions(scope_type, public_permissions)
        return super().validate(attributes)

@extend_schema_field(str)
class ScopeTypeField(RelatedField):
    """
    Serializer field for the `scope_type` to use the fully-qualified model name instead
    of the PK for input and output.
    """
    default_error_messages = {
        "not_found": _("Scope type '{value}' not found."),
        "invalid":   _("Invalid format: Expected a scope type string.")
    }

    def get_queryset(self):
        if not self.read_only:
            return ContentType.objects.all()

    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail("invalid")

        try:
            scope_type = content_type_for_model_string(data)
        except ContentType.DoesNotExist:
            self.fail("not_found", value=data)

        validate_scope_type(scope_type)
        return scope_type

    def to_representation(self, obj):
        return model_string_for_content_type(obj)
