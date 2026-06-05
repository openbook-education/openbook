# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django_filters.filters        import CharFilter
from django_filters.filterset      import FilterSet
from drf_spectacular.utils         import extend_schema
from rest_framework.viewsets       import ReadOnlyModelViewSet

from openbook.drf.flex_serializers import FlexFieldsModelSerializer
from openbook.drf.viewsets         import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets         import with_flex_fields_parameters
from ..models.language             import Language

class LanguageSerializer(FlexFieldsModelSerializer):
    __doc__ = "Language"

    class Meta:
        model  = Language
        fields = ("language", "name")
        expandable_fields = {}

class LanguageFilter(FilterSet):
    name = CharFilter(lookup_expr="icontains")

    class Meta:
        model  = Language
        fields = ("name",)

@extend_schema(
    extensions={
        "x-app-name":   "OpenBook Server",
        "x-model-name": "Available Languages",
    }
)
@with_flex_fields_parameters()
class LanguageViewSet(AllowAnonymousListRetrieveViewSetMixin, ReadOnlyModelViewSet):
    ___doc__ = "Available Languages"

    queryset           = Language.objects.all()
    serializer_class   = LanguageSerializer
    filterset_class    = LanguageFilter
    ordering           = ("language",)
    search_fields      = ("language", "name")