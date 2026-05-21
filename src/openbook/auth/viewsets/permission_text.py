# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from drf_spectacular.utils         import extend_schema
from django.contrib.auth.models    import Permission
from django_filters.filterset      import FilterSet
from django_filters.filters        import CharFilter
from rest_framework.viewsets       import ReadOnlyModelViewSet

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from openbook.drf.viewsets         import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets         import with_flex_fields_parameters
from ..models.permission_text      import PermissionText
from ..serializers.permission      import PermissionField
from ..utils                       import permission_for_perm_string

class PermissionTextSerializer(FlexFieldsModelSerializer):
    __doc__ = "Permission Label"

    parent = PermissionField()

    class Meta:
        model  = PermissionText
        fields = ("id", "language", "parent", "name")
        expandable_fields = {"parent": "openbook.auth.viewsets.permission.PermissionSerializer"}
    
class PermissionTextFilter(FilterSet):
    perm_string = CharFilter(label="Permission String", method="filter_perm_string")
    app         = CharFilter(label="App",   field_name="parent__content_type__app_label", lookup_expr="icontains")
    model       = CharFilter(label="Model", field_name="parent__content_type__model",     lookup_expr="icontains")
    codename    = CharFilter(label="Code",  field_name="parent__codename",                lookup_expr="icontains")
    name        = CharFilter(lookup_expr="icontains")

    class Meta:
        model  = PermissionText
        fields = ["app", "model", "codename", "language", "name"]
    
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
class PermissionTextViewSet(AllowAnonymousListRetrieveViewSetMixin, ReadOnlyModelViewSet):
    __doc__ = "Permission Labels"

    queryset         = PermissionText.objects.all()
    filterset_class  = PermissionTextFilter
    serializer_class = PermissionTextSerializer
    ordering         = ["parent__content_type__app_label", "parent__codename", "language__language"]

    search_fields = [
        "parent__content_type__app_label", "parent__codename",
        "language__language", "language__name",
        "name",
    ]