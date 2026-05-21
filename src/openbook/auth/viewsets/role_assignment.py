# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from drf_spectacular.utils         import extend_schema
from django_filters.filters        import CharFilter
from django_filters.filterset      import FilterSet
from rest_framework.viewsets       import ModelViewSet

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from openbook.drf.viewsets         import ModelViewSetMixin
from openbook.drf.viewsets         import with_flex_fields_parameters
from ..filters.mixins.audit        import CreatedModifiedByFilterMixin
from ..filters.mixins.scope        import ScopeFilterMixin
from ..models.role_assignment      import RoleAssignment
from ..serializers.mixins.scope    import ScopeTypeField
from ..serializers.role            import RoleField
from ..serializers.user            import UserField

class RoleAssignmentSerializer(FlexFieldsModelSerializer):
    __doc__ = "Role Assignment"

    scope_type  = ScopeTypeField()
    user        = UserField()
    role        = RoleField()
    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model = RoleAssignment

        fields = [
            "id", "scope_type", "scope_uuid",
            "role", "user", "assignment_method",
            "enrollment_method", "access_request",
            "is_active", "start_date", "end_date",
            "created_by", "created_at", "modified_by", "modified_at",
        ]

        read_only_fields = ["id", "created_at", "modified_at"]

        expandable_fields = {
            "user":              "openbook.auth.viewsets.user.UserSerializer",
            "role":              "openbook.auth.viewsets.role.RoleSerializer",
            "enrollment_method": "openbook.auth.viewsets.enrollment_method.EnrollmentMethodSerializer",
            "access_request":    "openbook.auth.viewsets.access_request.AccessRequestSerializer",
            "created_by":        "openbook.auth.viewsets.user.UserSerializer",
            "modified_by":       "openbook.auth.viewsets.user.UserSerializer",
        }

class RoleAssignmentFilter(ScopeFilterMixin, CreatedModifiedByFilterMixin, FilterSet):
    role = CharFilter(method="role_filter")
    user = CharFilter(method="user_filter")

    class Meta:
        model  = RoleAssignment
        fields = {
            **ScopeFilterMixin.Meta.fields,
            "start_date": ("exact", "lte", "gte"),
            "end_date":   ("exact", "lte", "gte"),
            "role": (),
            "user": (),
            "is_active": ("exact",),
            **CreatedModifiedByFilterMixin.Meta.fields,
        }

    def role_filter(self, queryset, name, value):
        return queryset.filter(role__slug=value)

    def user_filter(self, queryset, name, value):
        return queryset.filter(user__username=value)

@extend_schema(
    extensions={
        "x-app-name":   "User Management",
        "x-model-name": "Role Assignments",
    }
)
@with_flex_fields_parameters()
class RoleAssignmentViewSet(ModelViewSetMixin, ModelViewSet):
    __doc__ = "Users and their roles in a scope"

    queryset         = RoleAssignment.objects.all()
    filterset_class  = RoleAssignmentFilter
    serializer_class = RoleAssignmentSerializer
    ordering         = ["scope_type", "scope_uuid", "user__username", "role__slug"]

    search_fields = [
        "user__username", "user__first_name", "user__last_name", "user__email",
        "role__slug", "role__name", "role__description",
    ]
