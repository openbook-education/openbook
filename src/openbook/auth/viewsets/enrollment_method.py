# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django_filters.filters        import CharFilter
from django_filters.filterset      import FilterSet
from drf_spectacular.utils         import extend_schema
from drf_spectacular.utils         import inline_serializer
from rest_framework.decorators     import action
from rest_framework.response       import Response
from rest_framework.permissions    import AllowAny
from rest_framework.serializers    import CharField
from rest_framework.viewsets       import ModelViewSet

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from openbook.drf.viewsets         import ModelViewSetMixin
from openbook.drf.viewsets         import with_flex_fields_parameters
from ..filters.mixins.audit        import CreatedModifiedByFilterMixin
from ..filters.mixins.scope        import ScopeFilterMixin
from ..models.enrollment_method    import EnrollmentMethod
from .role_assignment              import RoleAssignmentSerializer
from ..serializers.mixins.scope    import ScopeTypeField
from ..serializers.role            import RoleField
from ..serializers.user            import UserField

class EnrollmentMethodSerializer(FlexFieldsModelSerializer):
    __doc__ = "Enrollment Method"

    scope_type  = ScopeTypeField()
    role        = RoleField()
    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model = EnrollmentMethod

        fields = [
            "id", "scope_type", "scope_uuid",
            "name", "description", "text_format",
            "role", "end_date", "duration_period", "duration_value",
            "passphrase", "is_active",
            "created_by", "created_at", "modified_by", "modified_at",
        ]

        read_only_fields = ["id", "created_at", "modified_at"]

        expandable_fields = {
            "role":        "openbook.auth.viewsets.role.RoleSerializer",
            "created_by":  "openbook.auth.viewsets.user.UserSerializer",
            "modified_by": "openbook.auth.viewsets.user.UserSerializer",
        }

class EnrollmentMethodFilter(ScopeFilterMixin, CreatedModifiedByFilterMixin, FilterSet):
    role = CharFilter(method="role_filter")

    class Meta:
        model  = EnrollmentMethod
        fields = {
            **ScopeFilterMixin.Meta.fields,
            "role":      (),
            "name":      ("exact",),
            "is_active": ("exact",),
            **CreatedModifiedByFilterMixin.Meta.fields,
        }

    def role_filter(self, queryset, name, value):
        return queryset.filter(role__slug=value)

@extend_schema(
    extensions={
        "x-app-name":   "User Management",
        "x-model-name": "Enrollment Methods",
    }
)
@with_flex_fields_parameters()
class EnrollmentMethodViewSet(ModelViewSetMixin, ModelViewSet):
    __doc__ = "Enrollment methods for self-registration"

    queryset         = EnrollmentMethod.objects.all()
    filterset_class  = EnrollmentMethodFilter
    serializer_class = EnrollmentMethodSerializer
    ordering         = ["scope_type", "scope_uuid", "name", "role__slug"]
    search_fields    = ["name", "description", "role__slug", "role__name", "role__description"]

    @extend_schema(
        operation_id = "auth_enrollment_method_enroll",
        summary      = "Enroll User",
        responses    = RoleAssignmentSerializer,
        request      = inline_serializer(
            name   = "EnrollActionRequestSerializer",
            fields = {
                "passphrase": CharField(required=False),
            }
        ),
    )
    @action(detail=True, methods=["put"], url_path="enroll", permission_classes=[AllowAny])
    def enroll(self, request, pk=None):
        """Enroll the current user with the selected enrollment method."""
        enrollment_method = self.get_object()

        kwargs = {
            "user":             request.user,
            "passphrase":       request.data.get("passphrase", None),
            "check_permission": True,
        }

        role_assignment = enrollment_method.enroll(**kwargs)
        serializer      = RoleAssignmentSerializer(role_assignment)

        return Response(serializer.data)
