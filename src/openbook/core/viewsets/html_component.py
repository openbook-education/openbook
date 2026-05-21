# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django_filters.filterset       import FilterSet
from drf_spectacular.utils          import extend_schema
from rest_framework.viewsets        import ReadOnlyModelViewSet

from openbook.drf.flex_serializers  import FlexFieldsModelSerializer
from openbook.drf.viewsets          import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets          import with_flex_fields_parameters
from ..models.html_component        import HTMLComponent

class HTMLComponentSerializer(FlexFieldsModelSerializer):
    __doc__ = "HTML Component"

    class Meta:
        model  = HTMLComponent

        fields = ["id", "library", "tag_name", "definitions"]
        read_only_fields = ["id", "definitions"]

        expandable_fields = {
            "library":     "openbook.core.viewsets.html_library.HTMLLibrarySerializer",
            "definitions": ("openbook.core.viewsets.html_component_definition.HTMLComponentDefinitionSerializer", {"many": True}),
        }

class HTMLComponentFilter(FilterSet):
    class Meta:
        model  = HTMLComponent
        fields = {
            "library__organization": ("icontains",),
            "library__name":         ("icontains",),
            "library__author":       ("icontains",),
            "tag_name":              ("icontains",),
        }

@extend_schema(
    extensions={
        "x-app-name":   "OpenBook Server",
        "x-model-name": "HTML Components",
    }
)
@with_flex_fields_parameters()
class HTMLComponentViewSet(AllowAnonymousListRetrieveViewSetMixin, ReadOnlyModelViewSet):
    __doc__ = "HTML Libraries"

    queryset         = HTMLComponent.objects.all()
    serializer_class = HTMLComponentSerializer
    filterset_class  = HTMLComponentFilter
    ordering         = ["library__organization", "library__name", "tag_name"]
    search_fields    = ["library__organization", "library__name", "library__author", "tag_name"]