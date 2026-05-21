# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from drf_spectacular.utils            import extend_schema
from django_filters.filterset         import FilterSet
from rest_framework.viewsets          import ReadOnlyModelViewSet

from openbook.drf.flex_serializers    import FlexFieldsModelSerializer
from openbook.drf.viewsets            import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets            import with_flex_fields_parameters
from ..filters.mixins.scope           import ScopeTypeFilterMixin
from ..filters.mixins.permission      import PermissionFilterMixin
from ..models.allowed_role_permission import AllowedRolePermission
from ..serializers.mixins.scope       import ScopeTypeField
from ..serializers.permission         import PermissionField

class AllowedRolePermissionSerializer(FlexFieldsModelSerializer):
    scope_type = ScopeTypeField()
    permission = PermissionField()

    class Meta:
        model  = AllowedRolePermission
        fields = ["id", "scope_type", "permission"]
        expandable_fields = {"permission": "openbook.auth.viewsets.permission.PermissionSerializer"}

class AllowedRolePermissionFilter(ScopeTypeFilterMixin, PermissionFilterMixin, FilterSet):
    class Meta:
        model  = AllowedRolePermission
        fields = {**ScopeTypeFilterMixin.Meta.fields, **PermissionFilterMixin.Meta.fields}
        permissions_field = "permission"

@extend_schema(
    extensions={
        "x-app-name":   "User Management",
        "x-model-name": "Allowed Role Permissions",
    }
)
@with_flex_fields_parameters()
class AllowedRolePermissionViewSet(AllowAnonymousListRetrieveViewSetMixin, ReadOnlyModelViewSet):
    __doc__ = "Allowed permissions for the roles of a given scope type"

    queryset         = AllowedRolePermission.objects.all().prefetch_related("scope_type", "permission")
    serializer_class = AllowedRolePermissionSerializer
    filterset_class  = AllowedRolePermissionFilter
    
    ordering = [
        "scope_type__app_label", "scope_type__model",
        "permission__content_type__app_label", "permission__codename",
    ]
    
    search_fields = [
        "scope_type__app_label", "scope_type__model",
        "permission__content_type__app_label", "permission__codename",
    ]
