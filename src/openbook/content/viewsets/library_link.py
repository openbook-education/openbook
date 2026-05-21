# OpenBook: Interactive Online Textbooks
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
from ..models.library_link              import LibraryLink


class LibraryLinkSerializer(FlexFieldsModelSerializer):
    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model = LibraryLink

        fields = [
            "id",
            "group", "course", "textbook",
            "created_by", "created_at", "modified_by", "modified_at",
        ]

        read_only_fields = [
            "id",
            "created_at", "modified_at",
        ]

        expandable_fields = {
            "group":       "openbook.content.viewsets.library_group.LibraryGroupSerializer",
            "course":      "openbook.content.viewsets.course.CourseSerializer",
            "textbook":    "openbook.content.viewsets.textbook.TextbookSerializer",
            "created_by":  "openbook.auth.viewsets.user.UserSerializer",
            "modified_by": "openbook.auth.viewsets.user.UserSerializer",
        }


class LibraryLinkFilter(CreatedModifiedByFilterMixin, FilterSet):
    class Meta:
        model  = LibraryLink
        fields = {
            "group":    ["exact"],
            "course":   ["exact"],
            "textbook": ["exact"],
            **CreatedModifiedByFilterMixin.Meta.fields,
        }


@extend_schema(
    extensions={
        "x-app-name":   "Content",
        "x-model-name": "Library Links",
    }
)
@with_flex_fields_parameters()
class LibraryLinkViewSet(ModelViewSetMixin, ModelViewSet):
    __doc__ = "Library Links"

    queryset         = LibraryLink.objects.all()
    filterset_class  = LibraryLinkFilter
    serializer_class = LibraryLinkSerializer
    ordering         = ["group", "id"]
    search_fields    = ["group__name", "course__name", "textbook__name"]
