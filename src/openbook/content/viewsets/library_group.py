# OpenBook: Interactive Online Textbooks
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django_filters.filterset               import FilterSet
from drf_spectacular.utils                  import extend_schema
from rest_framework.viewsets                import ModelViewSet

from openbook.auth.filters.mixins.audit     import CreatedModifiedByFilterMixin
from openbook.auth.filters.mixins.scope     import ScopedRolesFilterMixin
from openbook.auth.serializers.mixins.scope import ScopedRolesSerializerMixin
from openbook.auth.serializers.user         import UserField
from openbook.drf.flex_serializers          import FlexFieldsModelSerializer
from openbook.drf.viewsets                  import ModelViewSetMixin
from openbook.drf.viewsets                  import with_flex_fields_parameters
from ..models.library_group                 import LibraryGroup


class LibraryGroupSerializer(ScopedRolesSerializerMixin, FlexFieldsModelSerializer):
    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model = LibraryGroup

        fields = [
            "id", "slug",
            "name", "description", "text_format",
            "parent",
            "children", "textbooks", "courses", "links",
            *ScopedRolesSerializerMixin.Meta.fields,
            "created_by", "created_at", "modified_by", "modified_at",
        ]

        read_only_fields = [
            "id",
            "children", "textbooks", "courses", "links",
            *ScopedRolesSerializerMixin.Meta.read_only_fields,
            "created_at", "modified_at",
        ]

        expandable_fields = {
            **ScopedRolesSerializerMixin.Meta.expandable_fields,
            "parent":      "openbook.content.viewsets.library_group.LibraryGroupSerializer",
            "children":    ("openbook.content.viewsets.library_group.LibraryGroupSerializer", {"many": True}),
            "textbooks":   ("openbook.content.viewsets.textbook.TextbookSerializer", {"many": True}),
            "courses":     ("openbook.content.viewsets.course.CourseSerializer", {"many": True}),
            "links":       ("openbook.content.viewsets.library_link.LibraryLinkSerializer", {"many": True}),
            "created_by":  "openbook.auth.viewsets.user.UserSerializer",
            "modified_by": "openbook.auth.viewsets.user.UserSerializer",
        }


class LibraryGroupFilter(CreatedModifiedByFilterMixin, ScopedRolesFilterMixin, FilterSet):
    class Meta:
        model  = LibraryGroup
        fields = {
            "slug":     ["exact"],
            "name":     ["exact"],
            "parent":   ["exact"],
            **ScopedRolesFilterMixin.Meta.fields,
            **CreatedModifiedByFilterMixin.Meta.fields,
        }


@extend_schema(
    extensions={
        "x-app-name":   "Content",
        "x-model-name": "Library Groups",
    }
)
@with_flex_fields_parameters()
class LibraryGroupViewSet(ModelViewSetMixin, ModelViewSet):
    __doc__ = "Library Groups"

    queryset         = LibraryGroup.objects.all()
    filterset_class  = LibraryGroupFilter
    serializer_class = LibraryGroupSerializer
    ordering         = ["name"]
    search_fields    = ["slug", "name", "description"]
