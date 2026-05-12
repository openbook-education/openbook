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
from openbook.drf.viewsets              import AllowAnonymousListRetrieveViewSetMixin
from openbook.drf.viewsets              import ModelViewSetMixin
from openbook.drf.viewsets              import with_flex_fields_parameters
from ..models.textbook                  import Textbook


class TextbookSerializer(FlexFieldsModelSerializer):
    created_by  = UserField(read_only=True)
    modified_by = UserField(read_only=True)

    class Meta:
        model = Textbook

        fields = [
            "id", "slug",
            "name", "description", "text_format",
            "group",
            "pages", "used_in_courses", "library_links",
            "created_by", "created_at", "modified_by", "modified_at",
        ]

        read_only_fields = [
            "id",
            "pages", "used_in_courses", "library_links",
            "created_at", "modified_at",
        ]

        expandable_fields = {
            "group":          "openbook.content.viewsets.library_group.LibraryGroupSerializer",
            "pages":          ("openbook.content.viewsets.textbook_page.TextbookPageSerializer", {"many": True}),
            "used_in_courses": ("openbook.content.viewsets.course_material.CourseMaterialSerializer", {"many": True}),
            "library_links":  ("openbook.content.viewsets.library_link.LibraryLinkSerializer", {"many": True}),
            "created_by":     "openbook.auth.viewsets.user.UserSerializer",
            "modified_by":    "openbook.auth.viewsets.user.UserSerializer",
        }


class TextbookFilter(CreatedModifiedByFilterMixin, FilterSet):
    class Meta:
        model  = Textbook
        fields = {
            "slug":     ["exact"],
            "name":     ["exact"],
            "group":    ["exact"],
            **CreatedModifiedByFilterMixin.Meta.fields,
        }


@extend_schema(
    extensions={
        "x-app-name":   "Content",
        "x-model-name": "Textbooks",
    }
)
@with_flex_fields_parameters()
class TextbookViewSet(AllowAnonymousListRetrieveViewSetMixin, ModelViewSetMixin, ModelViewSet):
    __doc__ = "Textbooks"

    queryset         = Textbook.objects.all()
    filterset_class  = TextbookFilter
    serializer_class = TextbookSerializer
    ordering         = ["group", "position", "name"]
    search_fields    = ["slug", "name", "description"]
