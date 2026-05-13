# OpenBook: Interactive Online Textbooks - Server
# © 2026 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.utils.translation          import gettext_lazy as _

from openbook.admin                    import CustomModelAdmin
from openbook.admin                    import ImportExportModelResource
from openbook.auth.admin.mixins.audit  import created_modified_by_fields
from openbook.auth.admin.mixins.audit  import created_modified_by_fieldset
from openbook.auth.admin.mixins.audit  import created_modified_by_filter
from openbook.auth.admin.mixins.audit  import created_modified_by_related
from ..models.textbook_page            import TextbookPage


class TextbookPageResource(ImportExportModelResource):
    class Meta:
        model  = TextbookPage
        fields = [
            "id", "delete",
            "name", "description", "text_format",
            "textbook", "parent", "position",
        ]


class TextbookPageAdmin(CustomModelAdmin):
    model               = TextbookPage
    resource_classes    = [TextbookPageResource]
    list_display        = ["name", "textbook", "parent", "position", *created_modified_by_fields]
    list_display_links  = ["name"]
    list_filter         = ["textbook", "parent", *created_modified_by_filter]
    list_select_related = ["textbook", "parent", *created_modified_by_related]
    search_fields       = ["name", "textbook__name", "parent__name"]
    ordering            = ["textbook_id", "parent_id", "position", "name"]
    readonly_fields     = ["content", *created_modified_by_fields]

    fieldsets = [
        (None, {
            "fields": ["name", "textbook", ("parent", "position")],
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"],
        }),
        (_("Content"), {
            "classes": ["tab"],
            "fields": ["content"],
        }),
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": ["name", "textbook", ("parent", "position")],
        }),
        (_("Description"), {
            "classes": ["tab"],
            "fields": ["description", "text_format"],
        }),
    ]
