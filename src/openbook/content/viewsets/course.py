# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django_filters.filterset               import FilterSet
from drf_spectacular.utils                  import extend_schema
from rest_framework.viewsets                import ModelViewSet

from openbook.drf.flex_serializers          import FlexFieldsModelSerializer
from openbook.drf.viewsets                  import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets                  import ModelViewSetMixin
from openbook.drf.viewsets                  import with_flex_fields_parameters
from openbook.auth.filters.mixins.audit     import CreatedModifiedByFilterMixin
from openbook.auth.filters.mixins.scope     import ScopedRolesFilterMixin
from openbook.auth.serializers.mixins.scope import ScopedRolesSerializerMixin
from openbook.auth.serializers.user         import UserField
from ..models.course                        import Course

class CourseSerializer(ScopedRolesSerializerMixin, FlexFieldsModelSerializer):
    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model = Course

        fields = [
            "id", "slug",
            "name", "description", "text_format",
            "group", "is_template",
            "materials",
            *ScopedRolesSerializerMixin.Meta.fields,
            "created_by", "created_at", "modified_by", "modified_at",
        ]

        read_only_fields = [
            "id",
            "materials",
            *ScopedRolesSerializerMixin.Meta.read_only_fields,
            "created_at", "modified_at",
        ]

        expandable_fields = {
            **ScopedRolesSerializerMixin.Meta.expandable_fields,
            "group":       "openbook.content.viewsets.library_group.LibraryGroupSerializer",
            "materials":   ("openbook.content.viewsets.course_material.CourseMaterialSerializer", {"many": True}),
            "created_by":  "openbook.auth.viewsets.user.UserSerializer",
            "modified_by": "openbook.auth.viewsets.user.UserSerializer",
        }

class CourseFilter(CreatedModifiedByFilterMixin, ScopedRolesFilterMixin, FilterSet):
    class Meta:
        model  = Course
        fields = {
            "slug":        ["exact"],
            "name":        ["exact"],
            "group":       ["exact"],
            "is_template": ["exact"],
            **ScopedRolesFilterMixin.Meta.fields,
            **CreatedModifiedByFilterMixin.Meta.fields,
        }

@extend_schema(
    extensions={
        "x-app-name":   "Courses",
        "x-model-name": "Courses",
    }
)
@with_flex_fields_parameters()
class CourseViewSet(AllowAnonymousListRetrieveViewSetMixin, ModelViewSetMixin, ModelViewSet):
    __doc__ = "Courses"

    queryset         = Course.objects.all()
    filterset_class  = CourseFilter
    serializer_class = CourseSerializer
    ordering         = ["group", "position", "name"]
    search_fields    = ["slug", "name", "description"]
