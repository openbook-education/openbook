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
from ..models.course_material           import CourseMaterial


class CourseMaterialSerializer(FlexFieldsModelSerializer):
    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model = CourseMaterial

        fields = [
            "id",
            "course", "textbook",
            "position",
            "page_ranges",
            "created_by", "created_at", "modified_by", "modified_at",
        ]

        read_only_fields = [
            "id",
            "page_ranges",
            "created_at", "modified_at",
        ]

        expandable_fields = {
            "course":      "openbook.content.viewsets.course.CourseSerializer",
            "textbook":    "openbook.content.viewsets.textbook.TextbookSerializer",
            "page_ranges": ("openbook.content.viewsets.course_material_page_range.CourseMaterialPageRangeSerializer", {"many": True}),
            "created_by":  "openbook.auth.viewsets.user.UserSerializer",
            "modified_by": "openbook.auth.viewsets.user.UserSerializer",
        }


class CourseMaterialFilter(CreatedModifiedByFilterMixin, FilterSet):
    class Meta:
        model  = CourseMaterial
        fields = {
            "course":   ["exact"],
            "textbook": ["exact"],
            "position": ["exact", "lte", "gte"],
            **CreatedModifiedByFilterMixin.Meta.fields,
        }


@extend_schema(
    extensions={
        "x-app-name":   "Content",
        "x-model-name": "Course Materials",
    }
)
@with_flex_fields_parameters()
class CourseMaterialViewSet(ModelViewSetMixin, ModelViewSet):
    __doc__ = "Course Materials"

    queryset         = CourseMaterial.objects.all()
    filterset_class  = CourseMaterialFilter
    serializer_class = CourseMaterialSerializer
    ordering         = ["course", "position"]
    search_fields    = ["course__name", "textbook__name"]
