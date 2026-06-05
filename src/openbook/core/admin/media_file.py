# OpenBook: Interactive Online Textbooks
# © 2024 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.translation          import gettext_lazy as _
from import_export.fields              import Field

from openbook.admin                    import CustomModelAdmin
from openbook.admin                    import ImportExportModelResource
from openbook.auth.admin.mixins.audit  import created_modified_by_fields
from openbook.auth.admin.mixins.audit  import created_modified_by_fieldset
from openbook.auth.admin.mixins.audit  import created_modified_by_filter
from openbook.auth.admin.mixins.audit  import created_modified_by_related
from ..import_export.content_type      import ContentTypeForeignKeyWidget
from ..models.media_file               import MediaFile

class MediaFileInline(GenericTabularInline):
    model            = MediaFile
    fields           = ["file_data", "file_name", "file_size", "mime_type"]
    readonly_fields  = ["file_size", "mime_type"]
    ordering         = ["file_name"]
    extra            = 0
    show_change_link = True
    tab              = True

class MediaFileResource(ImportExportModelResource):
    content_type = Field(attribute="content_type", widget=ContentTypeForeignKeyWidget())

    class Meta:
        model = MediaFile
        fields = [
            "id", "delete",
            "content_type", "object_id",
            "file_data", "file_name", "file_size", "mime_type",
        ]

class MediaFileAdmin(CustomModelAdmin):
    model               = MediaFile
    resource_classes    = [MediaFileResource]
    list_display        = ["content_type", "object_id", "file_name", "file_size", "mime_type", *created_modified_by_fields]
    list_display_links  = ["content_type", "object_id", "file_name", "file_size", "mime_type"]
    list_filter         = ["file_size", "mime_type", *created_modified_by_filter]
    list_select_related = [*created_modified_by_related]
    readonly_fields     = ["file_name", "file_size", "mime_type", *created_modified_by_fields]
    search_fields       = ["file_name"]
    ordering            = ["content_type", "object_id", "file_name"]

    fieldsets = [
        (None, {
            "fields": ["content_type", "object_id"],
        }),
        (_("File"), {
            "classes": ["tab"],
            "fields": ["file_data", "file_name", "file_size", "mime_type"],
        }),
        created_modified_by_fieldset,
    ]

    add_fieldsets = [
        (None, {
            "fields": ["content_type", "object_id", "file_data"],
        }),
    ]
