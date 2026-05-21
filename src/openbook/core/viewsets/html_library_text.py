# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django_filters.filterset      import FilterSet
from drf_spectacular.utils         import extend_schema
from rest_framework.viewsets       import ReadOnlyModelViewSet

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from openbook.drf.viewsets         import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets         import with_flex_fields_parameters
from ..models.html_library         import HTMLLibraryText

class HTMLLibraryTextSerializer(FlexFieldsModelSerializer):
    __doc__ = "HTML Library Text"

    class Meta:
        model  = HTMLLibraryText
        fields = ["id", "parent", "language", "short_description"]
        read_only_fields = ["id"]

        expandable_fields = {
            "parent":      "openbook.core.viewsets.html_library.HTMLLibrarySerializer",
            "created_by":  "openbook.auth.viewsets.user.UserSerializer",
            "modified_by": "openbook.auth.viewsets.user.UserSerializer",
        }

class HTMLLibraryTextFilter(FilterSet):
    class Meta:
        model  = HTMLLibraryText
        fields = {
            "parent__id":           ("exact",),
            "parent__organization": ("icontains",),
            "parent__name":         ("icontains",),
            "parent__author":       ("icontains",),
            "language":             ("exact",),
            "short_description":    ("icontains",),
        }

@extend_schema(
    extensions={
        "x-app-name":   "OpenBook Server",
        "x-model-name": "HTML Library Texts",
    }
)
@with_flex_fields_parameters()
class HTMLLibraryTextViewSet(AllowAnonymousListRetrieveViewSetMixin, ReadOnlyModelViewSet):
    __doc__ = "HTML Libraries Texts"

    queryset         = HTMLLibraryText.objects.all().prefetch_related("parent")
    serializer_class = HTMLLibraryTextSerializer
    filterset_class  = HTMLLibraryTextFilter
    ordering         = ["parent__organization", "parent__name", "language"]
    search_fields    = ["parent__organization", "parent__name", "short_description"]