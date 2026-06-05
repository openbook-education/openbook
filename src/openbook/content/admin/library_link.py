# OpenBook: Interactive Online Textbooks
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.utils.translation          import gettext_lazy as _

from openbook.admin                    import CustomModelAdmin
from openbook.admin                    import ImportExportModelResource
from openbook.auth.admin.mixins.audit  import created_modified_by_fields
from openbook.auth.admin.mixins.audit  import created_modified_by_fieldset
from openbook.auth.admin.mixins.audit  import created_modified_by_filter
from openbook.auth.admin.mixins.audit  import created_modified_by_related
from ..models.library_link             import LibraryLink


class LibraryLinkResource(ImportExportModelResource):
    class Meta:
        model  = LibraryLink
        fields = [
            "id", "delete",
            "group", "course", "textbook",
        ]


class LibraryLinkAdmin(CustomModelAdmin):
    model               = LibraryLink
    resource_classes    = [LibraryLinkResource]
    list_display        = ["group", "course", "textbook", *created_modified_by_fields]
    list_display_links  = ["group", "course", "textbook"]
    list_filter         = ["group", "course", "textbook", *created_modified_by_filter]
    list_select_related = ["group", "course", "textbook", *created_modified_by_related]
    search_fields       = ["group__name", "course__name", "textbook__name"]
    ordering            = ["group",]
    readonly_fields     = [*created_modified_by_fields]

    fieldsets = [
        (None, {
            "fields": ["group", "course", "textbook",],
        }),
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": ["group", "course", "textbook",],
        }),
    ]
