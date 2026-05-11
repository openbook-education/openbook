# OpenBook: Interactive Online Textbooks - Server
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django_filters.filterset           import FilterSet
from drf_spectacular.utils              import extend_schema
from rest_framework.viewsets            import ModelViewSet

from openbook.auth.filters.mixins.audit import CreatedModifiedByFilterMixin
from openbook.auth.serializers.user     import UserField
from openbook.drf.flex_serializers      import FlexFieldsModelSerializer
from openbook.drf.viewsets              import ModelViewSetMixin
from openbook.drf.viewsets              import with_flex_fields_parameters
from ..models.course_material           import CourseMaterialPageRange


class CourseMaterialPageRangeSerializer(FlexFieldsModelSerializer):
    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model = CourseMaterialPageRange

        fields = [
            "id",
            "material", "start_page", "end_page",
            "position",
            "created_by", "created_at", "modified_by", "modified_at",
        ]

        read_only_fields = [
            "id",
            "created_at", "modified_at",
        ]

        expandable_fields = {
            "material":    "openbook.content.viewsets.course_material.CourseMaterialSerializer",
            "start_page":  "openbook.content.viewsets.textbook_page.TextbookPageSerializer",
            "end_page":    "openbook.content.viewsets.textbook_page.TextbookPageSerializer",
            "created_by":  "openbook.auth.viewsets.user.UserSerializer",
            "modified_by": "openbook.auth.viewsets.user.UserSerializer",
        }


class CourseMaterialPageRangeFilter(CreatedModifiedByFilterMixin, FilterSet):
    class Meta:
        model  = CourseMaterialPageRange
        fields = {
            "material":   ["exact"],
            "start_page": ["exact"],
            "end_page":   ["exact"],
            "position":   ["exact", "lte", "gte"],
            **CreatedModifiedByFilterMixin.Meta.fields,
        }


@extend_schema(
    extensions={
        "x-app-name":   "Content",
        "x-model-name": "Course Material Page Ranges",
    }
)
@with_flex_fields_parameters()
class CourseMaterialPageRangeViewSet(ModelViewSetMixin, ModelViewSet):
    __doc__ = "Course Material Page Ranges"

    queryset         = CourseMaterialPageRange.objects.all()
    filterset_class  = CourseMaterialPageRangeFilter
    serializer_class = CourseMaterialPageRangeSerializer
    ordering         = ["material", "position", "id"]
    search_fields    = ["material__course__name", "material__textbook__name", "start_page__name", "end_page__name"]
