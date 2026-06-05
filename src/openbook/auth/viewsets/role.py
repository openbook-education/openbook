# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django_filters.filterset      import FilterSet
from drf_spectacular.utils         import extend_schema
from rest_framework.viewsets       import ModelViewSet

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from openbook.drf.viewsets         import ModelViewSetMixin
from openbook.drf.viewsets         import with_flex_fields_parameters
from ..filters.mixins.audit        import CreatedModifiedByFilterMixin
from ..filters.mixins.scope        import ScopeFilterMixin
from ..models.role                 import Role
from ..validators                  import validate_permissions
from ..serializers.mixins.scope    import ScopeTypeField
from ..serializers.permission      import PermissionField
from ..serializers.user            import UserField

class RoleSerializer(FlexFieldsModelSerializer):
    __doc__ = "Role"

    scope_type  = ScopeTypeField()
    permissions = PermissionField(many=True)
    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model = Role

        fields = [
            "id", "scope_type", "scope_uuid", "slug",
            "name", "description", "text_format",
            "priority", "is_active", "permissions",
            "role_assignments", "enrollment_methods", "access_requests",
            "created_by", "created_at", "modified_by", "modified_at",
        ]

        read_only_fields = ["id", "created_at", "modified_at"]

        expandable_fields = {
            "permissions":        ("openbook.auth.viewsets.permission.PermissionSerializer",              {"many": True}),
            "created_by":         "openbook.auth.viewsets.user.UserSerializer",
            "modified_by":        "openbook.auth.viewsets.user.UserSerializer",
            "role_assignments":   ("openbook.auth.viewsets.role_assignment.RoleAssignmentSerializer",     {"many": True}),
            "enrollment_methods": ("openbook.auth.viewsets.enrollment_method.EnrollmentMethodSerializer", {"many": True}),
            "access_requests":    ("openbook.auth.viewsets.access_request.AccessRequestSerializer",       {"many": True}),
        }

    def validate(self, attributes):
        """Check that only allowed permissions are assigned."""
        scope_type  = attributes.get("scope_type", None)
        permissions = attributes.get("permissions", None)

        validate_permissions(scope_type, permissions)
        return attributes

class RoleFilter(ScopeFilterMixin, CreatedModifiedByFilterMixin, FilterSet):
    class Meta:
        model  = Role
        fields = {
            **ScopeFilterMixin.Meta.fields,
            "slug":      ("exact",),
            "name":      ("exact",),
            "priority":  ("exact", "lte", "gte"),
            "is_active": ("exact",),
            **CreatedModifiedByFilterMixin.Meta.fields,
        }

@extend_schema(
    extensions={
        "x-app-name":   "User Management",
        "x-model-name": "Roles",
    }
)
@with_flex_fields_parameters()
class RoleViewSet(ModelViewSetMixin, ModelViewSet):
    __doc__ = "User Roles Within a Scope"

    queryset         = Role.objects.all()
    filterset_class  = RoleFilter
    serializer_class = RoleSerializer
    ordering         = ["scope_type", "scope_uuid", "slug"]
    search_fields    = ["slug", "name", "description"]
