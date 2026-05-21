# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django_filters.filterset           import FilterSet
from drf_spectacular.utils              import extend_schema
from rest_framework.viewsets            import ReadOnlyModelViewSet

from openbook.auth.filters.mixins.audit import CreatedModifiedByFilterMixin
from openbook.auth.serializers.user     import UserField
from openbook.drf.flex_serializers      import FlexFieldsModelSerializer
from openbook.drf.viewsets              import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets              import with_flex_fields_parameters
from ..models.html_library              import HTMLLibraryVersion

class HTMLLibraryVersionSerializer(FlexFieldsModelSerializer):
    __doc__ = "HTML Library Version"

    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model  = HTMLLibraryVersion
        
        fields = [
            "id", "parent", "version", "dependencies", "frontend_url",
            "file_data", "file_name", "file_size", "mime_type",
            "components",
            "created_by", "created_at", "modified_by", "modified_at",
        ]
        
        read_only_fields = ["id", "components", "created_at", "modified_at"]

        expandable_fields = {
            "parent":      "openbook.core.viewsets.html_library.HTMLLibrarySerializer",
            "components":  ("openbook.core.viewsets.html_component_definition.HTMLComponentDefinitionSerializer", {"many": True}),
            "created_by":  "openbook.auth.viewsets.user.UserSerializer",
            "modified_by": "openbook.auth.viewsets.user.UserSerializer",
        }

class HTMLLibraryVersionFilter(FilterSet):
    class Meta:
        model  = HTMLLibraryVersion
        fields = {
            "parent__id":           ("exact",),
            "parent__organization": ("icontains",),
            "parent__name":         ("icontains",),
            "parent__author":       ("icontains",),
            "version":              ("icontains",),
            **CreatedModifiedByFilterMixin.Meta.fields,
        }

@extend_schema(
    extensions={
        "x-app-name":   "OpenBook Server",
        "x-model-name": "HTML Library Versions",
    }
)
@with_flex_fields_parameters()
class HTMLLibraryVersionViewSet(AllowAnonymousListRetrieveViewSetMixin, ReadOnlyModelViewSet):
    __doc__ = "HTML Library Versions"

    queryset         = HTMLLibraryVersion.objects.all().prefetch_related("parent")
    serializer_class = HTMLLibraryVersionSerializer
    filterset_class  = HTMLLibraryVersionFilter
    ordering         = ["parent__organization", "parent__name", "version"]
    search_fields    = ["parent__organization", "parent__name", "version", "dependencies"]