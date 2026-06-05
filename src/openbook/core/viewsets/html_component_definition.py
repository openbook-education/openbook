# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django_filters.filterset      import FilterSet
from drf_spectacular.utils         import extend_schema
from rest_framework.viewsets       import ReadOnlyModelViewSet

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from openbook.drf.viewsets         import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets         import with_flex_fields_parameters
from ..models.html_component       import HTMLComponentDefinition

class HTMLComponentDefinitionSerializer(FlexFieldsModelSerializer):
    __doc__ = "HTML Component Definition"

    class Meta:
        model  = HTMLComponentDefinition

        fields = ["id", "html_component", "library_version", "definition"]
        read_only_fields = ["id"]

        expandable_fields = {
            "html_component":  "openbook.core.viewsets.html_component.HTMLComponentSerializer",
            "library_version": "openbook.core.viewsets.html_library_version.HTMLLibraryVersionSerializer",
        }

class HTMLComponentDefinitionFilter(FilterSet):
    class Meta:
        model  = HTMLComponentDefinition
        fields = {
            "html_component__library__organization": ("icontains",),
            "html_component__library__name":         ("icontains",),
            "html_component__library__author":       ("icontains",),
            "html_component__tag_name":              ("icontains",),
            "library_version__version":              ("exact",),
        }

@extend_schema(
    extensions={
        "x-app-name":   "OpenBook Server",
        "x-model-name": "HTML Component Definitions",
    }
)
@with_flex_fields_parameters()
class HTMLComponentDefinitionViewSet(AllowAnonymousListRetrieveViewSetMixin, ReadOnlyModelViewSet):
    __doc__ = "HTML Libraries"

    queryset         = HTMLComponentDefinition.objects.all()
    serializer_class = HTMLComponentDefinitionSerializer
    filterset_class  = HTMLComponentDefinitionFilter
    
    ordering = [
        "html_component__library__organization",
        "html_component__library__name",
        "html_component__tag_name",
        "library_version__version",
    ]

    search_fields = [
        "html_component__library__organization",
        "html_component__library__name",
        "html_component__library__author",
        "html_component__tag_name",
        "library_version__version",
    ]