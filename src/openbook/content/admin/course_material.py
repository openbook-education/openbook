# OpenBook: Interactive Online Textbooks
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.admin              import TabularInline
from django.utils.translation          import gettext_lazy as _

from openbook.admin                    import CustomModelAdmin
from openbook.admin                    import ImportExportModelResource
from openbook.auth.admin.mixins.audit  import created_modified_by_fields
from openbook.auth.admin.mixins.audit  import created_modified_by_fieldset
from openbook.auth.admin.mixins.audit  import created_modified_by_filter
from openbook.auth.admin.mixins.audit  import created_modified_by_related
from ..models.course_material          import CourseMaterial
from ..models.course_material          import CourseMaterialPageRange


class _CourseMaterialPageRangeInline(TabularInline):
    model            = CourseMaterialPageRange
    extra            = 0
    show_change_link = True
    tab              = True
    fields           = ["start_page", "end_page", "position"]
    ordering         = ["position"]


class CourseMaterialResource(ImportExportModelResource):
    class Meta:
        model  = CourseMaterial
        fields = [
            "id", "delete",
            "course", "textbook", "position",
        ]


class CourseMaterialAdmin(CustomModelAdmin):
    model               = CourseMaterial
    resource_classes    = [CourseMaterialResource]
    list_display        = ["course", "textbook", "position", *created_modified_by_fields]
    list_display_links  = ["course", "textbook"]
    list_filter         = ["course", "textbook", *created_modified_by_filter]
    list_select_related = ["course", "textbook", *created_modified_by_related]
    search_fields       = ["course__name", "textbook__name"]
    ordering            = ["course", "position"]
    readonly_fields     = [*created_modified_by_fields]
    inlines             = [_CourseMaterialPageRangeInline]

    fieldsets = [
        (None, {
            "fields": ["course", "textbook", "position"],
        }),
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": ["course", "textbook", "position"],
        }),
    ]
