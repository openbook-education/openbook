# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django_filters.filterset           import FilterSet
from drf_spectacular.utils              import extend_schema
from drf_spectacular.utils              import extend_schema_field
from rest_framework.serializers         import SerializerMethodField
from rest_framework.viewsets            import ReadOnlyModelViewSet

from openbook.auth.filters.mixins.audit import CreatedModifiedByFilterMixin
from openbook.auth.serializers.user     import UserField
from openbook.drf.flex_serializers      import FlexFieldsModelSerializer
from openbook.drf.viewsets              import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets              import with_flex_fields_parameters
from ..models.html_library              import HTMLLibrary

class HTMLLibrarySerializer(FlexFieldsModelSerializer):
    __doc__ = "HTML Library"

    fqn         = SerializerMethodField()
    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model  = HTMLLibrary

        fields = [
            "id", "fqn", "organization", "name",
            "author", "license", "website", "coderepo", "bugtracker",
            "readme", "text_format", "published",
            "translations", "versions", "components",
            "created_by", "created_at", "modified_by", "modified_at",
        ]

        read_only_fields = ["id", "fqn", "translations", "versions", "components", "created_at", "modified_at"]

        expandable_fields = {
            "created_by":   "openbook.auth.viewsets.user.UserSerializer",
            "modified_by":  "openbook.auth.viewsets.user.UserSerializer",
            "translations": ("openbook.core.viewsets.html_library_text.HTMLLibraryTextSerializer",       {"many": True}),
            "components":   ("openbook.core.viewsets.html_component.HTMLComponentSerializer",            {"many": True}),
            "versions":     ("openbook.core.viewsets.html_library_version.HTMLLibraryVersionSerializer", {"many": True}),
        }
    
    @extend_schema_field(str)
    def get_fqn(self, obj):
        return obj.fqn() if hasattr(obj, "fqn") else ""

class HTMLLibraryFilter(FilterSet):
    class Meta:
        model  = HTMLLibrary
        fields = {
            "organization": ("icontains",),
            "name":         ("icontains",),
            "author":       ("icontains",),
            "license":      ("icontains",),
            "published":    ("exact",),
            **CreatedModifiedByFilterMixin.Meta.fields,
        }

@extend_schema(
    extensions={
        "x-app-name":   "OpenBook Server",
        "x-model-name": "HTML Libraries",
    }
)
@with_flex_fields_parameters()
class HTMLLibraryViewSet(AllowAnonymousListRetrieveViewSetMixin, ReadOnlyModelViewSet):
    __doc__ = "HTML Libraries"

    queryset         = HTMLLibrary.objects.all()
    serializer_class = HTMLLibrarySerializer
    filterset_class  = HTMLLibraryFilter
    ordering         = ["organization", "name"]
    search_fields    = ["organization", "name", "author", "license"]
