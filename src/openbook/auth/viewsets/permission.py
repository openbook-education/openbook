# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from drf_spectacular.utils         import extend_schema
from drf_spectacular.utils         import extend_schema_field
from django.contrib.auth.models    import Permission
from django_filters.filterset      import FilterSet
from django_filters.filters        import CharFilter
from rest_framework.viewsets       import ReadOnlyModelViewSet
from rest_framework.serializers    import SerializerMethodField

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from openbook.drf.viewsets         import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets         import with_flex_fields_parameters
from ..utils                       import app_label_for_permission
from ..utils                       import app_name_for_permission
from ..utils                       import model_for_permission
from ..utils                       import model_name_for_permission
from ..utils                       import perm_name_for_permission
from ..utils                       import perm_string_for_permission
from ..utils                       import permission_for_perm_string

class PermissionSerializer(FlexFieldsModelSerializer):
    __doc__ = "Permission"

    perm_string        = SerializerMethodField()
    perm_display_name  = SerializerMethodField()
    app                = SerializerMethodField()
    app_display_name   = SerializerMethodField()
    model              = SerializerMethodField()
    model_display_name = SerializerMethodField()

    class Meta:
        model = Permission

        fields = [
            "id",
            "name", "codename",
            "perm_string", "perm_display_name",
            "app", "app_display_name",
            "model", "model_display_name",
        ]

        read_only_fields  = ["id"]
        expandable_fields = {}
    
    @extend_schema_field(str)
    def get_perm_string(self, obj: Permission) -> str:
        return perm_string_for_permission(obj)

    @extend_schema_field(str)
    def get_perm_display_name(self, obj: Permission) -> str:
        return perm_name_for_permission(obj)

    @extend_schema_field(str)
    def get_app(self, obj: Permission) -> str:
        return app_label_for_permission(obj)

    @extend_schema_field(str)
    def get_app_display_name(self, obj: Permission) -> str:
        return app_name_for_permission(obj)

    @extend_schema_field(str)
    def get_model(self, obj: Permission) -> str:
        return model_for_permission(obj)

    @extend_schema_field(str)
    def get_model_display_name(self, obj: Permission) -> str:
        return model_name_for_permission(obj)

class PermissionFilter(FilterSet):
    perm_string = CharFilter(label="Permission String", method="filter_perm_string")
    app         = CharFilter(label="App",   field_name="content_type__app_label", lookup_expr="icontains")
    model       = CharFilter(label="Model", field_name="content_type__model",     lookup_expr="icontains")
    codename    = CharFilter(label="Code",  field_name="codename",                lookup_expr="icontains")

    class Meta:
        model  = Permission
        fields = ["app", "model", "codename"]
    
    def filter_perm_string(self, queryset, name, value):
        try:
            permission = permission_for_perm_string(value)
        except Permission.DoesNotExist:
            permission = None

        return queryset.filter(parent=permission) if permission else queryset.none()

@extend_schema(
    extensions={
        "x-app-name":   "User Management",
        "x-model-name": "Translated Permissions",
    }
)
@with_flex_fields_parameters()
class PermissionViewSet(AllowAnonymousListRetrieveViewSetMixin, ReadOnlyModelViewSet):
    __doc__ = "Permissions"

    queryset         = Permission.objects.all()
    filterset_class  = PermissionFilter
    serializer_class = PermissionSerializer
    ordering         = ["content_type__app_label", "codename"]
    search_fields    = ["content_type__app_label", "codename"]
