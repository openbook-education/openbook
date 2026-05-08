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
from rest_framework.decorators     import action
from rest_framework.response       import Response
from rest_framework.viewsets       import ModelViewSet

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from openbook.drf.viewsets         import ModelViewSetMixin
from openbook.drf.viewsets         import with_flex_fields_parameters
from ..filters.mixins.audit        import CreatedModifiedByFilterMixin
from ..filters.mixins.scope        import ScopeFilterMixin
from ..models.access_request       import AccessRequest
from ..serializers.mixins.scope    import ScopeTypeField
from ..serializers.role            import RoleField
from ..serializers.user            import UserField

class AccessRequestSerializer(FlexFieldsModelSerializer):
    __doc__ = "Access Request"

    scope_type  = ScopeTypeField()
    user        = UserField()
    role        = RoleField()
    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model = AccessRequest

        fields = [
            "id", "scope_type", "scope_uuid",
            "user", "role",
            "end_date", "duration_period", "duration_value",
            "decision", "decision_date",
            "created_by", "created_at", "modified_by", "modified_at",
        ]

        read_only_fields = ["id", "decision_date", "created_at", "modified_at"]

        expandable_fields = {
            "user":        "openbook.auth.viewsets.user.UserSerializer",
            "role":        "openbook.auth.viewsets.role.RoleSerializer",
            "created_by":  "openbook.auth.viewsets.user.UserSerializer",
            "modified_by": "openbook.auth.viewsets.user.UserSerializer",
        }

class AccessRequestFilter(ScopeFilterMixin, CreatedModifiedByFilterMixin, FilterSet):
    role = CharFilter(method="role_filter")
    user = CharFilter(method="user_filter")

    class Meta:
        model  = AccessRequest
        fields = {
            **ScopeFilterMixin.Meta.fields,
            "role":          (),
            "user":          (),
            "decision":      ("exact",),
            "decision_date": ("exact", "lte", "gte"),
            **CreatedModifiedByFilterMixin.Meta.fields,
        }

    def role_filter(self, queryset, name, value):
        return queryset.filter(role__slug=value)

    def user_filter(self, queryset, name, value):
        return queryset.filter(user__username=value)

@extend_schema(
    extensions={
        "x-app-name":   "User Management",
        "x-model-name": "Access Requests",
    }
)
@with_flex_fields_parameters()
class AccessRequestViewSet(ModelViewSetMixin, ModelViewSet):
    __doc__ = "Access requests to get a scoped role assigned"

    queryset         = AccessRequest.objects.all()
    filterset_class  = AccessRequestFilter
    serializer_class = AccessRequestSerializer
    ordering         = ["scope_type", "scope_uuid", "user__username", "role__slug"]

    search_fields = [
        "user__username", "user__first_name", "user__last_name", "user__email",
        "role__slug", "role__name", "role__description",
    ]

    @extend_schema(
        operation_id = "auth_access_requests_accept",
        request      = None,
        responses    = AccessRequestSerializer,
        summary      = "Accept",
    )
    @action(methods=["put"], detail=True)   # PUT since an existing access request is updated
    def accept(self, request, pk):
        """Accept the request."""
        access_request = self.get_object()
        access_request.accept(permission_user=request.user)
        return Response(AccessRequestSerializer(instance=access_request).data)

    @extend_schema(
        operation_id = "auth_access_requests_deny",
        request      = None,
        responses    = AccessRequestSerializer,
        summary      = "Deny",
    )
    @action(methods=["put"], detail=True)   # PUT since an existing access request is updated
    def deny(self, request, pk):
        """Deny the request."""
        access_request = self.get_object()
        access_request.deny(permission_user=request.user)
        return Response(AccessRequestSerializer(instance=access_request).data)
